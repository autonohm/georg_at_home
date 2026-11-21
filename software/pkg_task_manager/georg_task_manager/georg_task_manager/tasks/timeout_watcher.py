import time
import asyncio


async def wait_for_flag(interface, flag_name, timeout):

    start = time.time()

    while not getattr(interface, flag_name):

        await asyncio.sleep(0.1)

        if time.time() - start > timeout:
            return False

    return True


def as_asyncio_future(rclpy_future, loop=None):

    loop = loop or asyncio.get_event_loop()
    async_future = loop.create_future()

    def _on_done(f):

        def _resolve():
            if not async_future.done():
                try:
                    async_future.set_result(f.result())
                except Exception as e:
                    if not async_future.done():
                        async_future.set_exception(e)

        if loop.is_closed():
            return

        try:
            loop.call_soon_threadsafe(_resolve)
        except RuntimeError:
            pass

    rclpy_future.add_done_callback(_on_done)
    return async_future


async def wait_for_action_result(action_client, goal_msg, timeout, abort_check=None):

    if not action_client.wait_for_server(timeout_sec=2.0):
        return None

    send_goal_future = action_client.send_goal_async(goal_msg)
    goal_handle = await as_asyncio_future(send_goal_future)

    if not goal_handle.accepted:
        return None

    result_future = goal_handle.get_result_async()
    async_result_future = as_asyncio_future(result_future)

    start = time.time()

    while not async_result_future.done():

        if abort_check is not None and abort_check():
            cancel_future = goal_handle.cancel_goal_async()
            await as_asyncio_future(cancel_future)  # auf Cancel-Bestätigung warten
            return None

        if time.time() - start > timeout:
            cancel_future = goal_handle.cancel_goal_async()
            await as_asyncio_future(cancel_future)  # auf Cancel-Bestätigung warten
            return None

        await asyncio.sleep(0.1)

    return async_result_future.result().result

async def wait_for_service_result(service_client, request, timeout: float = 10.0, abort_check=None, availability_timeout: float = 2.0, poll_interval: float = 0.05,):
    """Ruft einen ROS2-Service (z.B aus pib-backend !) auf und wartet auf das Ergebnis.

    Gibt die Response zurück, oder None bei: Service nicht verfügbar,
    Timeout, Abbruch oder Fehler im Service.
    """
    loop = asyncio.get_running_loop()

    # 1. Service erreichbar?
    deadline = loop.time() + availability_timeout
    while not service_client.service_is_ready():
        if abort_check is not None and abort_check():
            return None
        if loop.time() >= deadline:
            return None
        await asyncio.sleep(poll_interval)

    # 2. Aufruf
    future = service_client.call_async(request)
    deadline = loop.time() + timeout
    while not future.done():
        if (abort_check and abort_check()) or loop.time() > deadline:
            future.cancel()
            service_client.remove_pending_request(future)
            return None
        await asyncio.sleep(poll_interval)

    try:
        return future.result()
    except Exception as exc:
        print(f"[SERVICE] Call failed: {exc}")
        return None
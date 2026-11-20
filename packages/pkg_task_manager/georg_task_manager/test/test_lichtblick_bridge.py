"""P4: the task manager can be operated completely through foxglove_bridge.

This test talks the same WebSocket protocol as Lichtblick (foxglove.websocket.v1):
it calls the task manager services and subscribes to the status topic through the
bridge, i.e. exactly what the Lichtblick panel does. The panel UI itself is tested in
packages/pkg_viz/lichtblick_panel/test (node --test).

Needs ROS, foxglove_bridge and the built workspace; skipped otherwise (GEORG_ROS_TESTS=1).
"""

import asyncio
import json
import os
import random
import struct
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: E402, I100

if os.environ.get('GEORG_ROS_TESTS') != '1' or 'rclpy' in conftest.STUBBED:
    pytest.skip('ROS integration tests: set GEORG_ROS_TESTS=1 in a ROS environment',
                allow_module_level=True)

from georg_task_manager_msgs.msg import MissionStatus  # noqa: E402, I100
from georg_task_manager_msgs.srv import CancelMission, ListMissions, StartMission  # noqa: E402
from georg_task_manager_msgs.srv import Instruct, SetMode  # noqa: E402
from rclpy.serialization import deserialize_message, serialize_message  # noqa: E402
from ros_helpers import _spawn, _stop, NS  # noqa: E402
from std_msgs.msg import String  # noqa: E402
import websockets  # noqa: E402

PORT = random.randint(18000, 18999)
LICHTBLICK_SUBPROTOCOLS = ['foxglove.websocket.v1', 'foxglove.sdk.v1']
SERVICES = {'start': StartMission, 'cancel': CancelMission, 'list_missions': ListMissions,
            'set_mode': SetMode, 'instruct': Instruct}


@pytest.fixture(scope='module')
def env(ros_profile):
    import ros_helpers
    e = ros_helpers.make_env(ros_profile)
    e['GEORG_LLM_URL'] = 'http://127.0.0.1:9'    # no LLM in these tests
    return e


@pytest.fixture(scope='module')
def foxglove_bridge(env, bridge):
    # min_qos_depth 10 like in compose (pkg_viz): otherwise status messages that follow each
    # other within milliseconds (last Burr steps) are dropped in the bridge's subscription
    proc = _spawn(['ros2', 'launch', 'foxglove_bridge', 'foxglove_bridge_launch.xml',
                   f'port:={PORT}', 'min_qos_depth:=10'],
                  os.path.join(env['TMP'], 'foxglove_bridge.log'), env)
    time.sleep(4.0)
    yield proc
    _stop(proc)


class LichtblickLikeClient:
    """Minimal Foxglove WebSocket client: services + one subscription."""

    def __init__(self, ws):
        self.ws = ws
        self.services = {}
        self.channels = {}
        self.statuses = []
        self.plans = []
        self._types = {}
        self._responses = {}
        self._call_id = 0
        self._reader = asyncio.ensure_future(self._read())

    async def _read(self):
        async for raw in self.ws:
            if isinstance(raw, str):
                msg = json.loads(raw)
                if msg['op'] == 'advertiseServices':
                    self.services.update({s['name']: s for s in msg['services']})
                elif msg['op'] == 'advertise':
                    self.channels.update({c['topic']: c for c in msg['channels']})
                continue
            op = raw[0]
            if op == 0x01:                            # message data
                sub_id = struct.unpack_from('<I', raw, 1)[0]
                payload = raw[1 + 4 + 8:]
                if self._types.get(sub_id, MissionStatus) is String:
                    self.plans.append(json.loads(deserialize_message(payload, String).data))
                else:
                    self.statuses.append(deserialize_message(payload, MissionStatus))
            elif op == 0x03:                          # service call response
                service_id, call_id, enc_len = struct.unpack_from('<III', raw, 1)
                payload = raw[1 + 12 + enc_len:]
                self._responses[call_id] = payload

    async def wait_for(self, predicate, timeout=20.0):
        end = time.monotonic() + timeout
        while not predicate():
            assert time.monotonic() < end, 'timeout'
            await asyncio.sleep(0.05)

    async def subscribe(self, topic, msg_type=MissionStatus, sub_id=1):
        await self.wait_for(lambda: topic in self.channels)
        self._types[sub_id] = msg_type
        await self.ws.send(json.dumps({'op': 'subscribe', 'subscriptions': [
            {'id': sub_id, 'channelId': self.channels[topic]['id']}]}))

    async def call(self, name, request):
        full = f'{NS}/task_manager/{name}'
        await self.wait_for(lambda: full in self.services)
        self._call_id += 1
        call_id, enc = self._call_id, b'cdr'
        header = struct.pack('<BIII', 0x02, self.services[full]['id'], call_id, len(enc))
        await self.ws.send(header + enc + serialize_message(request))
        await self.wait_for(lambda: call_id in self._responses)
        return deserialize_message(self._responses.pop(call_id), SERVICES[name].Response)


async def _session(test):
    # same subprotocol offer as Lichtblick 1.30 (FoxgloveWebSocketPlayer); foxglove_bridge 3.x
    # only accepts foxglove.sdk.v1
    async with websockets.connect(f'ws://127.0.0.1:{PORT}', max_size=None,
                                  subprotocols=LICHTBLICK_SUBPROTOCOLS) as ws:
        assert ws.subprotocol in LICHTBLICK_SUBPROTOCOLS
        client = LichtblickLikeClient(ws)
        try:
            await test(client)
        finally:
            client._reader.cancel()


def test_mission_list_start_and_live_status_through_the_bridge(foxglove_bridge, mocks, client):
    mocks.run('all_ok')

    async def scenario(c):
        await c.subscribe(f'{NS}/task_manager/status')
        missions = await c.call('list_missions', ListMissions.Request())
        assert 'mock_test' in missions.mission_ids
        response = await c.call('start', StartMission.Request(mission_id='mock_test'))
        assert response.accepted, response.reason
        app = response.burr_app_id
        await c.wait_for(lambda: any(s.burr_app_id == app and s.state == MissionStatus.SUCCEEDED
                                     for s in c.statuses), timeout=30)
        running = [s for s in c.statuses if s.burr_app_id == app
                   and s.state == MissionStatus.RUNNING]
        # status updates on every Burr step: every task of mock_test shows up
        tasks = [s.current_task for s in running]
        for task in ('Listening(DOORBELL)', 'Gesture', 'NavigateObject', 'ReturnToIdle'):
            direct = [(x.state, x.current_task, x.step) for x in client.statuses
                      if x.burr_app_id == app]
            assert task in tasks, (direct, [(s.state, s.current_task, s.step) for s in c.statuses])
        assert len({s.step for s in running}) >= 4

    asyncio.run(_session(scenario))


def test_abort_through_the_bridge(foxglove_bridge, mocks):
    mocks.run('abort')

    async def scenario(c):
        await c.subscribe(f'{NS}/task_manager/status')
        response = await c.call('start', StartMission.Request(mission_id='mock_test'))
        assert response.accepted, response.reason
        app = response.burr_app_id
        await c.wait_for(lambda: any(s.burr_app_id == app and s.current_task == 'NavigateObject'
                                     for s in c.statuses), timeout=20)
        await asyncio.sleep(1.0)
        cancel = await c.call('cancel', CancelMission.Request())
        assert cancel.accepted, cancel.reason
        await c.wait_for(lambda: any(s.burr_app_id == app and s.state == MissionStatus.ABORTED
                                     for s in c.statuses), timeout=10)

    asyncio.run(_session(scenario))


def test_rejection_reason_reaches_the_panel(foxglove_bridge, mocks):
    mocks.run('unreachable')

    async def scenario(c):
        response = await c.call('start', StartMission.Request(mission_id='mock_test'))
        assert not response.accepted
        assert 'nav/drive_route' in response.reason

    asyncio.run(_session(scenario))


def test_operating_mode_and_instruction_through_the_bridge(foxglove_bridge):
    async def scenario(c):
        await c.subscribe(f'{NS}/task_manager/plan', String, sub_id=2)
        await c.wait_for(lambda: any(p.get('mode') == 'mission' for p in c.plans))
        response = await c.call('set_mode', SetMode.Request(mode='llm'))
        assert response.accepted and response.mode == 'llm'
        await c.wait_for(lambda: any(p.get('mode') == 'llm' for p in c.plans))
        # no LLM endpoint in this test: the reason must reach the panel
        response = await c.call('instruct', Instruct.Request(text='greet the guest'))
        assert not response.accepted and 'not reachable' in response.reason
        assert (await c.call('set_mode', SetMode.Request(mode='mission'))).accepted

    asyncio.run(_session(scenario))

"""pib_bridge: Georg's stack <-> pib-backend, with a fixed allowlist.

One process, two ROS domains: the stack domain (ROS_DOMAIN_ID: 30 in sim, 0 on the robot) and
the pib-backend domain (PIB_BACKEND_DOMAIN_ID, 0). Nothing else crosses - in particular no
drive or motor commands.

Stack side (served by this node):
    speech/say    georg_speech_msgs/Say     -> pib-backend /play_audio_from_speech (join=true)
    audio/listen  georg_speech_msgs/Listen  SPEECH: pib-backend action /record_audio
                                            (RecordAudio: waits for speech, stops after a
                                            pause, speech-to-text) -> transcript (as in branch
                                            pib_backend_integration, leakmpf); DOORBELL:
                                            PIB_DOORBELL_TOPIC (std_msgs/Bool), none by
                                            default -> not detected
Forwarded read-only from pib-backend to the stack, only if the domains differ (on the robot
both are 0 and the stack sees pib-backend directly):
    parameter forward_topics: ["topic|package/msg/Type", ...]  (default: head camera + detections)
"""
import os
import threading
import time

from datatypes.action import RecordAudio
from datatypes.srv import PlayAudioFromSpeech
from georg_speech_msgs.action import Listen, Say
import rclpy
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.context import Context
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rosidl_runtime_py.utilities import get_message
from std_msgs.msg import Bool

DEFAULT_FORWARD = [
    '/oak/rgb/image_raw/compressed|sensor_msgs/msg/CompressedImage',
    '/detections/face_detection_yunet_160x120|datatypes/msg/DetectionArray',
    '/detections/yolov6n_coco_640x640|datatypes/msg/DetectionArray',
    '/detections/hand_tracking|datatypes/msg/DetectionArray',
]


class Backend:
    """Node in the pib-backend domain: service client and speech topics."""

    def __init__(self, context, doorbell_topic):
        self.node = Node('georg_pib_bridge', context=context)
        cb = ReentrantCallbackGroup()
        self.say = self.node.create_client(PlayAudioFromSpeech, '/play_audio_from_speech',
                                           callback_group=cb)
        self.record = ActionClient(self.node, RecordAudio, '/record_audio', callback_group=cb)
        self.lock = threading.Lock()
        self.doorbell_events = []
        if doorbell_topic:
            self.node.create_subscription(Bool, doorbell_topic, self._on_doorbell, 10,
                                          callback_group=cb)

    def _on_doorbell(self, msg):
        if msg.data:
            with self.lock:
                self.doorbell_events.append(time.monotonic())

    def first_event_after(self, events, since):
        with self.lock:
            return next((t for t in events if t >= since), None)


class PibBridge:
    """Node in the stack domain: actions speech/say, audio/listen and forwarded topics."""

    def __init__(self, stack_ctx, backend, forward_from, same_domain):
        self.node = Node('pib_bridge', context=stack_ctx)
        p = self.node.declare_parameter
        self.gender = p('default_gender', 'M1').value
        self.language = p('default_language', 'de').value
        self.say_timeout = p('say_timeout_s', 60.0).value
        # RecordAudio: pause after speech that ends the utterance, speech-to-text engine
        # (values of branch pib_backend_integration)
        self.silent_after = p('listen_silent_after_s', 1.0).value
        self.stt_engine = p('stt_engine', 'local_whisper').value
        forward = list(p('forward_topics', DEFAULT_FORWARD).value)
        self.backend = backend
        cb = ReentrantCallbackGroup()
        accept = lambda _goal: GoalResponse.ACCEPT    # noqa: E731
        cancel = lambda _goal: CancelResponse.ACCEPT  # noqa: E731
        self._servers = [
            ActionServer(self.node, Say, 'speech/say', self._on_say, goal_callback=accept,
                         cancel_callback=cancel, callback_group=cb),
            ActionServer(self.node, Listen, 'audio/listen', self._on_listen,
                         goal_callback=accept, cancel_callback=cancel, callback_group=cb),
        ]
        self._forwards = []
        if same_domain:
            self.node.get_logger().info('stack and pib-backend share a domain: no forwarding')
        else:
            for entry in forward:
                topic, _, type_name = entry.partition('|')
                self._forward(forward_from, topic.strip(), type_name.strip())

    def _forward(self, backend_node, topic, type_name):
        try:
            msg_type = get_message(type_name)
        except (AttributeError, ModuleNotFoundError, ValueError) as exc:
            self.node.get_logger().error(f'forward {topic}: unknown type {type_name}: {exc}')
            return
        pub = self.node.create_publisher(msg_type, topic, qos_profile_sensor_data)
        sub = backend_node.create_subscription(msg_type, topic, pub.publish,
                                               qos_profile_sensor_data, raw=True)
        self._forwards.append((pub, sub))
        self.node.get_logger().info(f'forwarding {topic} ({type_name}) pib-backend -> stack')

    def _on_say(self, goal_handle):
        goal = goal_handle.request
        result = Say.Result()
        if not self.backend.say.wait_for_service(timeout_sec=3.0):
            goal_handle.abort()
            result.success, result.message = False, '/play_audio_from_speech not available'
            return result
        req = PlayAudioFromSpeech.Request()
        req.speech = goal.text
        req.gender = goal.gender or self.gender
        req.language = goal.language or self.language
        req.join = True
        future = self.backend.say.call_async(req)
        deadline = time.monotonic() + self.say_timeout
        while not future.done():
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.success, result.message = False, 'canceled'
                return result
            if time.monotonic() > deadline:
                goal_handle.abort()
                result.success, result.message = False, 'pib-backend did not answer in time'
                return result
            time.sleep(0.05)
        goal_handle.succeed()
        result.success, result.message = True, 'spoken by pib-backend'
        return result

    def _on_listen(self, goal_handle):
        goal = goal_handle.request
        if goal.mode == Listen.Goal.MODE_SPEECH:
            return self._listen_speech(goal_handle)
        start = time.monotonic()
        deadline = start + (goal.timeout_sec if goal.timeout_sec > 0 else 60.0)
        result = Listen.Result()
        while time.monotonic() < deadline:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return result
            if self.backend.first_event_after(self.backend.doorbell_events, start) is not None:
                result.detected, result.confidence = True, 1.0
                goal_handle.succeed()
                return result
            time.sleep(0.05)
        goal_handle.succeed()
        return result

    def _listen_speech(self, goal_handle):
        """Speech -> pib-backend /record_audio; detected if it understood any text."""
        result = Listen.Result()
        if not self.backend.record.wait_for_server(timeout_sec=3.0):
            self.node.get_logger().error('/record_audio of pib-backend not available')
            goal_handle.abort()
            return result
        before = goal_handle.request.timeout_sec if goal_handle.request.timeout_sec > 0 else 8.0
        rec = RecordAudio.Goal()
        rec.max_silent_seconds_before = float(before)
        rec.max_silent_seconds_after = float(self.silent_after)
        if 'stt_engine' in rec.get_fields_and_field_types():
            rec.stt_engine = self.stt_engine
        send = self.backend.record.send_goal_async(rec)
        # speech may start at the end of the wait and last a while, then speech-to-text
        deadline = time.monotonic() + before + 40.0
        handle, result_future = None, None
        while time.monotonic() < deadline:
            if goal_handle.is_cancel_requested:
                if handle is not None:
                    handle.cancel_goal_async()
                goal_handle.canceled()
                return result
            if handle is None and send.done():
                handle = send.result()
                if not handle.accepted:
                    goal_handle.abort()
                    return result
                result_future = handle.get_result_async()
            if result_future is not None and result_future.done():
                text = (result_future.result().result.transcribed_text or '').strip()
                result.detected, result.confidence = bool(text), 1.0 if text else 0.0
                result.transcript = text
                self.node.get_logger().info(f'heard: {text!r}')
                goal_handle.succeed()
                return result
            time.sleep(0.05)
        if handle is not None:
            handle.cancel_goal_async()
        goal_handle.abort()
        return result


def main():
    """Start both domains and spin them in their own executors."""
    stack_domain = int(os.environ.get('ROS_DOMAIN_ID', '0'))
    backend_domain = int(os.environ.get('PIB_BACKEND_DOMAIN_ID', '0'))
    stack_ctx, backend_ctx = Context(), Context()
    rclpy.init(context=stack_ctx, domain_id=stack_domain)
    rclpy.init(context=backend_ctx, domain_id=backend_domain)
    doorbell = os.environ.get('PIB_DOORBELL_TOPIC', '')
    backend = Backend(backend_ctx, doorbell)
    bridge = PibBridge(stack_ctx, backend, backend.node, stack_domain == backend_domain)
    bridge.node.get_logger().info(
        f'pib_bridge ready: stack domain {stack_domain}, pib-backend domain {backend_domain}, '
        f'doorbell {doorbell or "none"}')
    executors = []
    for node, ctx in ((bridge.node, stack_ctx), (backend.node, backend_ctx)):
        ex = MultiThreadedExecutor(num_threads=4, context=ctx)
        ex.add_node(node)
        executors.append(ex)
    threads = [threading.Thread(target=ex.spin, daemon=True) for ex in executors]
    for t in threads:
        t.start()
    try:
        while all(t.is_alive() for t in threads):
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for ex in executors:
            ex.shutdown()
        rclpy.try_shutdown(context=stack_ctx)
        rclpy.try_shutdown(context=backend_ctx)


if __name__ == '__main__':
    main()

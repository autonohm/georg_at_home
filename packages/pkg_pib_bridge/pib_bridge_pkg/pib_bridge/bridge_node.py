"""pib_bridge: Georg's stack <-> pib-backend, with a fixed allowlist.

One process, two ROS domains: the stack domain (ROS_DOMAIN_ID: 30 in sim, 0 on the robot) and
the pib-backend domain (PIB_BACKEND_DOMAIN_ID, 0). Nothing else crosses - in particular no
drive or motor commands.

Stack side (served by this node):
    speech/say    georg_speech_msgs/Say     -> pib-backend /play_audio_from_speech (join=true)
    audio/listen  georg_speech_msgs/Listen  SPEECH: /speech_detected (std_msgs/Bool) of
                                            pib-backend, transcript from /chat_messages
                                            (is_user); DOORBELL: parameter doorbell_topic
                                            (std_msgs/Bool), none by default -> not detected
Forwarded read-only from pib-backend to the stack, only if the domains differ (on the robot
both are 0 and the stack sees pib-backend directly):
    parameter forward_topics: ["topic|package/msg/Type", ...]  (default: head camera + detections)
"""
import os
import threading
import time

from datatypes.msg import ChatMessage
from datatypes.srv import PlayAudioFromSpeech
from georg_speech_msgs.action import Listen, Say
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
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
        self.lock = threading.Lock()
        self.speech_events = []          # monotonic times of speech_detected == True
        self.doorbell_events = []
        self.user_messages = []          # (monotonic time, text)
        self.node.create_subscription(Bool, '/speech_detected', self._on_speech, 10,
                                      callback_group=cb)
        self.node.create_subscription(ChatMessage, '/chat_messages', self._on_chat, 10,
                                      callback_group=cb)
        if doorbell_topic:
            self.node.create_subscription(Bool, doorbell_topic, self._on_doorbell, 10,
                                          callback_group=cb)

    def _on_speech(self, msg):
        if msg.data:
            with self.lock:
                self.speech_events.append(time.monotonic())

    def _on_doorbell(self, msg):
        if msg.data:
            with self.lock:
                self.doorbell_events.append(time.monotonic())

    def _on_chat(self, msg):
        if msg.is_user and msg.content:
            with self.lock:
                self.user_messages.append((time.monotonic(), msg.content))

    def first_event_after(self, events, since):
        with self.lock:
            return next((t for t in events if t >= since), None)

    def transcript_after(self, since):
        with self.lock:
            texts = [text for t, text in self.user_messages if t >= since]
        return texts[-1] if texts else ''


class PibBridge:
    """Node in the stack domain: actions speech/say, audio/listen and forwarded topics."""

    def __init__(self, stack_ctx, backend, forward_from, same_domain):
        self.node = Node('pib_bridge', context=stack_ctx)
        p = self.node.declare_parameter
        self.gender = p('default_gender', 'M1').value
        self.language = p('default_language', 'de').value
        self.say_timeout = p('say_timeout_s', 60.0).value
        self.transcript_wait = p('transcript_wait_s', 6.0).value
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
        start = time.monotonic()
        deadline = start + (goal.timeout_sec if goal.timeout_sec > 0 else 60.0)
        speech = goal.mode == Listen.Goal.MODE_SPEECH
        events = self.backend.speech_events if speech else self.backend.doorbell_events
        result = Listen.Result()
        while time.monotonic() < deadline:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return result
            if self.backend.first_event_after(events, start) is not None:
                result.detected, result.confidence = True, 1.0
                if speech:
                    # the transcript comes as a chat message once speech-to-text is done
                    end = time.monotonic() + self.transcript_wait
                    while time.monotonic() < end and not result.transcript:
                        result.transcript = self.backend.transcript_after(start)
                        time.sleep(0.1)
                goal_handle.succeed()
                return result
            time.sleep(0.05)
        goal_handle.succeed()
        result.detected, result.confidence = False, 0.0
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

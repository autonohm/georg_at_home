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
Robot only (stack and pib-backend share the domain, profile real):
    pib/pose      georg_gesture_msgs/PibPose   named pose/sequence (pkg_pib_model
                                               config/pib_poses.yaml) -> /apply_joint_trajectory;
                                               every angle checked against pib_limits.yaml (pose
                                               rejected if outside); DRY RUN unless
                                               PIB_POSE_ENABLE=1 (only logs what it would send)
In sim the fake motors of pkg_pib_model serve pib/pose; the bridge does not.

No sensor data crosses (camera, detections, joint states): in sim the robot must only
see the simulation, like it can only move simulated motors. On the robot the stack and
pib-backend share domain 0 and see each other directly; in mcap the recording plays.
"""
import os
import threading
import time

from datatypes.action import RecordAudio
from datatypes.srv import ApplyJointTrajectory, PlayAudioFromSpeech
from georg_gesture_msgs.action import PibPose
from georg_speech_msgs.action import Listen, Say
import rclpy
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.context import Context
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Bool
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import yaml


class Backend:
    """Node in the pib-backend domain: service client and speech topics."""

    def __init__(self, context, doorbell_topic):
        self.node = Node('georg_pib_bridge', context=context)
        cb = ReentrantCallbackGroup()
        self.say = self.node.create_client(PlayAudioFromSpeech, '/play_audio_from_speech',
                                           callback_group=cb)
        self.record = ActionClient(self.node, RecordAudio, '/record_audio', callback_group=cb)
        self.joints = self.node.create_client(ApplyJointTrajectory, '/apply_joint_trajectory',
                                              callback_group=cb)
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
    """Node in the stack domain: actions speech/say and audio/listen."""

    def __init__(self, stack_ctx, backend, serve_poses=False):
        self.node = Node('pib_bridge', context=stack_ctx)
        p = self.node.declare_parameter
        self.gender = p('default_gender', 'M1').value
        self.language = p('default_language', 'de').value
        self.say_timeout = p('say_timeout_s', 60.0).value
        # wait until pib-backend has finished speaking (robot). false without a loudspeaker:
        # audio_player then never finishes and blocks (Q37); missions then go on while speaking
        self.say_join = os.environ.get('PIB_SAY_JOIN', 'true').lower() != 'false'
        # RecordAudio: pause after speech that ends the utterance, speech-to-text engine
        # (values of branch pib_backend_integration)
        self.silent_after = p('listen_silent_after_s', 1.0).value
        self.stt_engine = p('stt_engine', 'local_whisper').value
        self.backend = backend
        cb = ReentrantCallbackGroup()
        accept = lambda _goal: GoalResponse.ACCEPT    # noqa: E731
        cancel = lambda _goal: CancelResponse.ACCEPT  # noqa: E731
        self.poses_file = os.environ.get('PIB_POSES_FILE', '/config/pib_poses.yaml')
        self.limits_file = os.environ.get('PIB_LIMITS_FILE', '/config/pib_limits.yaml')
        self.pose_enable = os.environ.get('PIB_POSE_ENABLE', '0') == '1'
        self.pose_speed = 1.0          # rad/s assumed for waiting between the steps
        self._servers = [
            ActionServer(self.node, Say, 'speech/say', self._on_say, goal_callback=accept,
                         cancel_callback=cancel, callback_group=cb),
            ActionServer(self.node, Listen, 'audio/listen', self._on_listen,
                         goal_callback=accept, cancel_callback=cancel, callback_group=cb),
        ]
        if serve_poses:
            self._servers.append(ActionServer(
                self.node, PibPose, 'pib/pose', self._on_pose, goal_callback=accept,
                cancel_callback=cancel, callback_group=cb))
            self.node.get_logger().info(
                'pib/pose -> /apply_joint_trajectory: '
                + ('ENABLED (real servos)' if self.pose_enable else 'DRY RUN (PIB_POSE_ENABLE=1 '
                   'sends to the servos)'))

    def _load(self):
        with open(self.poses_file, encoding='utf-8') as f:
            poses = yaml.safe_load(f) or {}
        with open(self.limits_file, encoding='utf-8') as f:
            limits = yaml.safe_load(f) or {}
        return poses.get('poses') or {}, poses.get('sequences') or {}, limits

    @staticmethod
    def check_limits(pose, limits):
        """Return the list of violations (empty = pose allowed)."""
        lo, hi = limits.get('default_min', -1.5708), limits.get('default_max', 1.5708)
        bad = []
        for motor, rad in pose.items():
            mn, mx = (limits.get('motors') or {}).get(motor, (lo, hi))
            if not mn <= float(rad) <= mx:
                bad.append(f'{motor}={float(rad):.2f} not in [{mn:.2f}, {mx:.2f}]')
        return bad

    def _on_pose(self, goal_handle):
        """Named pose or sequence to the real servos, after the limit check."""
        result = PibPose.Result()
        try:
            poses, sequences, limits = self._load()
        except (OSError, yaml.YAMLError) as exc:
            goal_handle.abort()
            result.message = f'cannot read poses/limits: {exc}'
            return result
        name = goal_handle.request.pose
        steps = sequences.get(name) or ([name] if name in poses else None)
        if steps is None:
            goal_handle.abort()
            result.message = f'unknown pose {name!r}'
            return result
        for step in steps:
            bad = self.check_limits(poses.get(step) or {}, limits)
            if bad:
                goal_handle.abort()
                result.message = f'pose {step} rejected: ' + '; '.join(bad)
                self.node.get_logger().error(result.message)
                return result
        last = {}
        for step in steps:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.message = f'canceled at {step}'
                return result
            pose = {m: float(r) for m, r in (poses.get(step) or {}).items()}
            feedback = PibPose.Feedback()
            feedback.state = step
            goal_handle.publish_feedback(feedback)
            if not self.pose_enable:
                self.node.get_logger().info(f'DRY RUN pose {step}: {pose}')
                continue
            if not self._send_joints(pose):
                goal_handle.abort()
                result.message = f'pib-backend did not accept pose {step}'
                return result
            move = max((abs(r - last.get(m, 0.0)) for m, r in pose.items()), default=0.0)
            time.sleep(min(5.0, move / self.pose_speed + 0.3))
            last.update(pose)
        goal_handle.succeed()
        result.success = True
        done = 'sent to the servos' if self.pose_enable else 'checked (dry run, nothing sent)'
        result.message = f'pose {name} {done}'
        return result

    def _send_joints(self, pose):
        if not self.backend.joints.wait_for_service(timeout_sec=3.0):
            self.node.get_logger().error('/apply_joint_trajectory of pib-backend not available')
            return False
        req = ApplyJointTrajectory.Request()
        jt = JointTrajectory()
        jt.joint_names = list(pose)
        point = JointTrajectoryPoint()
        point.positions = [pose[m] for m in jt.joint_names]
        jt.points = [point]
        req.joint_trajectory = jt
        future = self.backend.joints.call_async(req)
        end = time.monotonic() + 10.0
        while not future.done() and time.monotonic() < end:
            time.sleep(0.05)
        return future.done() and future.result() is not None and future.result().successful

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
        req.join = self.say_join
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
    # pib/pose only on the robot (same domain): in sim the fake motors serve it
    bridge = PibBridge(stack_ctx, backend, serve_poses=stack_domain == backend_domain)
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

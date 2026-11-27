#!/usr/bin/env python3
"""Continuously turn pib's head toward the nearest face.

Standalone version of the voice assistant's "turn toward the speaker" logic
(voice_assistant/attention.py), but running as a closed loop: the camera sits
in the head, so a face offset in the image is relative to the *current* head
pose. Each update moves the head by a fraction (``--gain``) of that offset.

Inputs (all already published on the robot):
  /detections/face_detection_yunet_160x120    YuNet face boxes from the OAK-D's
                                              own NPU, ~10 Hz. Started on the
                                              camera via start_model while this
                                              runs, released on exit.
  /face_center                                Haar face offset [x, y] in px from
                                              image centre, [0, 0] = no face.
                                              ~2 Hz fallback, used only while
                                              YuNet is not delivering.
  /joint_states                               current head angles (radians)

Output: apply_joint_trajectory service on turn_head_motor / tilt_forward_motor.

Run inside a ROS container, e.g. via tools/face_follow.sh. Ctrl+C to stop.
"""

from __future__ import annotations

import argparse
import math
import signal
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions

from datatypes.msg import DetectionArray
from datatypes.srv import ApplyJointTrajectory, StartModel, StopModel
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32MultiArray
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

PAN_MOTOR = "turn_head_motor"
TILT_MOTOR = "tilt_forward_motor"

# OAK-D Lite colour camera preview, same constants as pib_hermes_config.attention.
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
HFOV_DEG = 69.0

YUNET_MODEL_ID = "face_detection_yunet_160x120"
YUNET_TOPIC = "detections/" + YUNET_MODEL_ID
# Owner name for the camera's ref-counted start_model/stop_model: other users
# of YuNet keep it running when we release ours.
MODEL_OWNER = "face_follower"
# Haar is ignored while YuNet has published (even "no face") this recently.
YUNET_FRESH_SECONDS = 1.0


def offset_to_deg(offset_px: float, frame_width: float) -> float:
    """Pixel offset from the image centre -> angle in degrees (pinhole model)."""
    focal_px = (frame_width / 2.0) / math.tan(math.radians(HFOV_DEG / 2.0))
    return math.degrees(math.atan2(offset_px, focal_px))


class FaceFollower(Node):
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__("face_follower")
        self.args = args
        self._lock = threading.Lock()
        # Latest face as angular offset (deg) from the camera axis + timestamp.
        self._face: tuple[float, float, float] | None = None  # (dx, dy, t)
        self._joint_deg: dict[str, float] = {}
        # Last commanded target; used when joint_states is unavailable.
        self._target = {PAN_MOTOR: None, TILT_MOTOR: None}
        self._last_command = 0.0
        self._last_seen = time.monotonic()
        self._homed = True
        self._yunet_last_msg = 0.0
        self._yunet_requested = False

        self._client = self.create_client(
            ApplyJointTrajectory, "apply_joint_trajectory"
        )
        self._start_model = self.create_client(StartModel, "start_model")
        self._stop_model = self.create_client(StopModel, "stop_model")
        if not args.no_yunet:
            self._request_yunet()
        self.create_subscription(
            Float32MultiArray, "face_center", self._on_face_center, 10
        )
        self.create_subscription(DetectionArray, YUNET_TOPIC, self._on_yunet, 10)
        self.create_subscription(JointState, "joint_states", self._on_joints, 10)
        self.create_timer(1.0 / args.rate, self._step)
        self.get_logger().info(
            f"following faces: gain={args.gain} deadband={args.deadband}deg "
            f"tilt={'off' if args.no_tilt else 'on'}"
        )

    # ---- YuNet on the camera ----------------------------------------------

    def _request_yunet(self) -> None:
        if not self._start_model.wait_for_service(timeout_sec=5.0):
            self.get_logger().warning("start_model service not found; using Haar only")
            return
        request = StartModel.Request()
        request.model_id = YUNET_MODEL_ID
        request.shaves = 0  # the model's compiled default
        request.owner = MODEL_OWNER
        self._yunet_requested = True
        self.get_logger().info(
            "starting YuNet on the camera (pipeline rebuild, a few seconds)..."
        )
        # Async: the camera answers only after the rebuild; Haar covers meanwhile.
        self._start_model.call_async(request).add_done_callback(self._on_yunet_started)

    def _on_yunet_started(self, future) -> None:
        try:
            response = future.result()
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warning(f"YuNet start failed: {exc}; using Haar")
            return
        if response.success:
            self.get_logger().info(f"YuNet: {response.message}")
        else:
            self.get_logger().warning(f"YuNet not started: {response.message}; using Haar")

    def release_yunet(self) -> None:
        """Drop our claim on YuNet. The camera keeps it if someone else uses it."""
        if not self._yunet_requested:
            return
        self._yunet_requested = False
        if not self._stop_model.service_is_ready():
            return
        request = StopModel.Request()
        request.model_id = YUNET_MODEL_ID
        request.owner = MODEL_OWNER
        future = self._stop_model.call_async(request)
        # The camera acts on the request even if we stop waiting for the reply.
        rclpy.spin_until_future_complete(self, future, timeout_sec=3.0)
        self.get_logger().info("released YuNet")

    # ---- sensor callbacks -------------------------------------------------

    def _on_face_center(self, msg: Float32MultiArray) -> None:
        if time.monotonic() - self._yunet_last_msg < YUNET_FRESH_SECONDS:
            return  # YuNet is live; don't mix two detectors' estimates
        data = list(msg.data)
        if len(data) < 2 or (data[0] == 0.0 and data[1] == 0.0):
            return  # [0, 0] is the "no face" sentinel
        dx = offset_to_deg(float(data[0]), FRAME_WIDTH)
        dy = offset_to_deg(float(data[1]), FRAME_WIDTH)  # same focal length
        self._note_face(dx, dy, "haar")

    def _on_yunet(self, msg: DetectionArray) -> None:
        self._yunet_last_msg = time.monotonic()
        width = float(msg.frame_width or FRAME_WIDTH)
        height = float(msg.frame_height or FRAME_HEIGHT)
        faces = list(msg.detections)
        if not faces:
            return
        best = max(
            faces, key=lambda d: (d.x_max - d.x_min) * (d.y_max - d.y_min)
        )
        cx = (best.x_min + best.x_max) / 2.0 - width / 2.0
        cy = height / 2.0 - (best.y_min + best.y_max) / 2.0  # up is positive
        self._note_face(offset_to_deg(cx, width), offset_to_deg(cy, width), "yunet")

    def _note_face(self, dx: float, dy: float, source: str) -> None:
        with self._lock:
            self._face = (dx, dy, time.monotonic())
        if self.args.verbose:
            self.get_logger().info(f"{source}: dx={dx:+.1f} dy={dy:+.1f} deg")

    def _on_joints(self, msg: JointState) -> None:
        with self._lock:
            for name, pos in zip(msg.name, msg.position):
                if name in (PAN_MOTOR, TILT_MOTOR):
                    self._joint_deg[name] = math.degrees(pos)

    # ---- control loop -----------------------------------------------------

    def _current(self, motor: str) -> float:
        target = self._target[motor]
        if target is not None:
            # Servos lag; joint_states may still show the old pose for a while.
            # Trust our own last command for a short window after sending it.
            if time.monotonic() - self._last_command < self.args.settle:
                return target
        return self._joint_deg.get(motor, target if target is not None else 0.0)

    def _step(self) -> None:
        now = time.monotonic()
        if now - self._last_command < self.args.min_interval:
            # Let the servo move first: frames captured mid-turn would each add
            # the same correction again and overshoot. Keep the newest face.
            return
        with self._lock:
            face = self._face
            self._face = None  # consume: each observation moves the head once

        if face is None or now - face[2] > self.args.max_age:
            if (
                self.args.return_home is not None
                and not self._homed
                and now - self._last_seen > self.args.return_home
            ):
                self.get_logger().info("face lost, returning to centre")
                self._send({PAN_MOTOR: 0.0, TILT_MOTOR: 0.0})
                self._homed = True
            return

        self._last_seen = now
        self._homed = False
        dx, dy, _ = face
        goals: dict[str, float] = {}

        if abs(dx) > self.args.deadband:
            pan = self._current(PAN_MOTOR) + self.args.pan_sign * self.args.gain * dx
            goals[PAN_MOTOR] = max(-self.args.pan_limit, min(self.args.pan_limit, pan))

        if not self.args.no_tilt and abs(dy) > self.args.deadband:
            tilt = self._current(TILT_MOTOR) + self.args.tilt_sign * self.args.gain * dy
            goals[TILT_MOTOR] = max(self.args.tilt_min, min(self.args.tilt_max, tilt))

        if goals:
            self._send(goals)

    def _send(self, goals: dict[str, float]) -> None:
        if not self._client.service_is_ready():
            self.get_logger().warning(
                "apply_joint_trajectory not ready", throttle_duration_sec=5.0
            )
            return
        # One request per motor, exactly like the voice assistant does.
        for motor, deg in goals.items():
            request = ApplyJointTrajectory.Request()
            trajectory = JointTrajectory()
            trajectory.joint_names = [motor]
            point = JointTrajectoryPoint()
            point.positions = [math.radians(deg)]
            trajectory.points = [point]
            request.joint_trajectory = trajectory
            self._client.call_async(request)
            self._target[motor] = deg
        self._last_command = time.monotonic()
        self.get_logger().info(
            "  ".join(f"{m}={d:+.1f}deg" for m, d in goals.items())
        )


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--gain", type=float, default=0.6,
                   help="fraction of the offset corrected per update (0..1)")
    p.add_argument("--deadband", type=float, default=3.0,
                   help="ignore offsets smaller than this many degrees")
    p.add_argument("--rate", type=float, default=10.0, help="control loop Hz")
    p.add_argument("--max-age", type=float, default=0.6,
                   help="ignore face observations older than this (s)")
    p.add_argument("--settle", type=float, default=0.4,
                   help="trust last command over joint_states for this long (s)")
    p.add_argument("--min-interval", type=float, default=0.3,
                   help="minimum time between head commands (s)")
    p.add_argument("--no-tilt", action="store_true", help="pan only")
    p.add_argument("--no-yunet", action="store_true",
                   help="don't start YuNet on the camera; use Haar face_center only")
    # Verified on the robot: face right of centre -> negative turn_head_motor,
    # face above centre -> positive tilt_forward_motor.
    p.add_argument("--pan-sign", type=float, default=-1.0, choices=[1.0, -1.0],
                   help="flip if the head turns away from your face")
    p.add_argument("--tilt-sign", type=float, default=1.0, choices=[1.0, -1.0],
                   help="flip if the head nods away from your face")
    p.add_argument("--pan-limit", type=float, default=80.0, help="+/- degrees")
    p.add_argument("--tilt-min", type=float, default=-20.0)
    p.add_argument("--tilt-max", type=float, default=30.0)
    p.add_argument("--return-home", type=float, default=None, metavar="SECONDS",
                   help="re-centre the head after no face for this long")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv if argv is not None else [])


def face_follow(argv=None) -> None:
    args = parse_args(argv)
    # Handle signals ourselves: rclpy's handler shuts the context down at once,
    # and then we could no longer tell the camera to release YuNet.
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)

    def interrupt(_signum, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, interrupt)
    signal.signal(signal.SIGTERM, interrupt)
    node = FaceFollower(args)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        try:
            node.release_yunet()
        except Exception as exc:  # noqa: BLE001
            node.get_logger().warning(f"could not release YuNet: {exc}")
            return -1
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
            return 0


if __name__ == "__main__":
    face_follow()

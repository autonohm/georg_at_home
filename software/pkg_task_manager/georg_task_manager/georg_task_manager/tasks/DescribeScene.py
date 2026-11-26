import asyncio
import statistics
from collections import Counter

from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

from .base import BaseTask
from .priority import TaskPriority
from datatypes.msg import DetectionArray

TOPIC = "/detections/yolov6n_coco_640x640"

# matches the publisher: RELIABLE + VOLATILE
QOS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
)

NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
                6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}

IRREGULAR_PLURALS = {
    "person": "people", "knife": "knives", "scissors": "scissors",
    "skis": "skis", "sheep": "sheep", "mouse": "mice",
    "wine glass": "wine glasses", "sandwich": "sandwiches",
    "couch": "couches", "bench": "benches", "broccoli": "broccoli",
}


def plural(label, count):
    if count == 1:
        return label
    if label in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[label]
    if label.endswith(("s", "x", "ch", "sh")):
        return label + "es"
    return label + "s"


def count_phrase(label, count):
    if count == 1:
        return ("an " if label[0] in "aeiou" else "a ") + label
    return f"{NUMBER_WORDS.get(count, str(count))} {plural(label, count)}"


def join_natural(parts):
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def horizontal_position(det, frame_width):
    cx = (det.x_min + det.x_max) / 2 / frame_width
    if cx < 1 / 3:
        return "on the left"
    if cx < 2 / 3:
        return "in the middle"
    return "on the right"


class DescribeScene(BaseTask):
    """Collects detections for a short time, stabilizes them and stores a
    brief two-sentence English description in state.scene_description
    (and the single sentences in state.scene_sentences)."""

    def __init__(self, priority=TaskPriority.LOW, collect_seconds=1.5,
                 min_score=0.5, max_position_labels=2):
        super().__init__("DescribeScene", priority)
        self.collect_seconds = collect_seconds
        self.min_score = min_score
        self.max_position_labels = max_position_labels

    async def _collect_frames(self, robot, state):
        frames = []
        sub = robot.node.create_subscription(
            DetectionArray, TOPIC, frames.append, QOS)
        try:
            waited, step = 0.0, 0.05
            while waited < self.collect_seconds:
                if getattr(state, "abort_requested", False):
                    return None
                await asyncio.sleep(step)
                waited += step
        finally:
            robot.node.destroy_subscription(sub)
        return frames

    def _stabilize(self, frames):
        """Median count per label over all frames (removes flicker);
        positions come from the most recent frame."""
        per_frame = [
            Counter(d.label for d in f.detections if d.score >= self.min_score)
            for f in frames
        ]
        labels = set().union(*per_frame)
        last = frames[-1]
        result = {}
        for label in labels:
            n = int(round(statistics.median(c.get(label, 0) for c in per_frame)))
            if n <= 0:
                continue
            dets = sorted(
                (d for d in last.detections
                 if d.label == label and d.score >= self.min_score),
                key=lambda d: d.score, reverse=True,
            )[:n]
            if dets:
                result[label] = dets
        return result, (last.frame_width or 1920)

    def _build_sentences(self, stable, frame_width):
        if not stable:
            return ["I can't see anything I recognize right now."]

        # people first, then most frequent
        ordered = sorted(stable.items(),
                         key=lambda kv: (kv[0] != "person", -len(kv[1]), kv[0]))

        sentence1 = "I can see " + join_natural(
            [count_phrase(label, len(dets)) for label, dets in ordered]) + "."

        clauses = []
        for label, dets in ordered[:self.max_position_labels]:
            positions = list(dict.fromkeys(
                horizontal_position(d, frame_width)
                for d in sorted(dets, key=lambda d: d.x_min)))
            if len(dets) == 1:
                clauses.append(f"the {label} is {positions[0]}")
            else:
                clauses.append(
                    f"the {plural(label, 2)} are {join_natural(positions)}")
        sentence2 = clauses[0][0].upper() + clauses[0][1:]
        if len(clauses) > 1:
            sentence2 += ", and " + ", and ".join(clauses[1:])
        sentence2 += "."

        return [sentence1, sentence2]

    async def run(self, robot, state):
        frames = await self._collect_frames(robot, state)
        if not frames:
            state.scene_sentences = ["I could not get an image to describe."]
            state.scene_description = state.scene_sentences[0]
            return False

        stable, frame_width = self._stabilize(frames)
        state.scene_sentences = self._build_sentences(stable, frame_width)
        state.scene_description = " ".join(state.scene_sentences)
        return True
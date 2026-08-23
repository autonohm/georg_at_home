"""Classify doorbell and speech sounds with Google's pretrained YAMNet."""

import csv
import numpy as np
import tensorflow_hub as hub
import tensorflow as tf


class YamnetDoorbellClassifier:
    """Interpret selected AudioSet classes as doorbell or speech evidence."""

    def __init__(
        self,
        doorbell_threshold=0.30,
        speech_threshold=0.30,
        speech_max_threshold=0.25,
    ) -> None:
        """Load YAMNet and resolve relevant class indices.

        Thresholds operate on mean class scores across all YAMNet frames.
        Doorbell detection additionally requires speech to remain below
        ``speech_max_threshold`` to reduce voice-triggered false positives.
        """
        # TensorFlow Hub caches the downloaded model outside this class.
        self.model = hub.load("https://tfhub.dev/google/yamnet/1")
        self.doorbell_threshold = doorbell_threshold
        self.speech_threshold = speech_threshold
        self.speech_max_threshold = speech_max_threshold

        class_map_path = self.model.class_map_path().numpy().decode("utf-8")
        self.class_names = self._load_class_names(class_map_path)

        self.doorbell_indices = self._find_indices(["Doorbell", "Ding-dong", "Knock", "Tap"])
        self.speech_indices = self._find_indices(["Speech", "Conversation", "Human voice"])

    def classify(self, waveform_16khz_float: np.ndarray) -> dict:
        """Return aggregate predictions for a mono 16 kHz waveform.

        The returned mapping keeps ``detected`` as a compatibility alias for
        ``doorbell_detected`` and includes the globally strongest AudioSet
        class for diagnostics.
        """
        scores, _, _ = self.model(waveform_16khz_float.astype(np.float32))
        # Collapse time frames so a clip has one score per AudioSet class.
        mean_scores = scores.numpy().mean(axis=0)

        doorbell_score = self._max_score(mean_scores, self.doorbell_indices)
        speech_score = self._max_score(mean_scores, self.speech_indices)

        top_index = int(np.argmax(mean_scores))

        doorbell_detected = (
            doorbell_score >= self.doorbell_threshold
            and speech_score <= self.speech_max_threshold
        )

        speech_detected = speech_score >= self.speech_threshold

        return {
            "detected": doorbell_detected,
            "doorbell_detected": doorbell_detected,
            "speech_detected": speech_detected,
            "doorbell_score": float(doorbell_score),
            "speech_score": float(speech_score),
            "top_class": self.class_names[top_index],
            "top_score": float(mean_scores[top_index]),
        }

    def _load_class_names(self, path: str) -> list[str]:
        """Read display names from YAMNet's bundled class-map CSV."""
        with tf.io.gfile.GFile(path) as csvfile:
            return [row["display_name"] for row in csv.DictReader(csvfile)]

    def _find_indices(self, names: list[str]) -> list[int]:
        """Find classes containing any configured label fragment."""
        return [
            i
            for i, class_name in enumerate(self.class_names)
            if any(name.lower() in class_name.lower() for name in names)
        ]

    def _max_score(self, scores: np.ndarray, indices: list[int]) -> float:
        """Return the strongest selected score, or zero for no class match."""
        return float(np.max(scores[indices])) if indices else 0.0

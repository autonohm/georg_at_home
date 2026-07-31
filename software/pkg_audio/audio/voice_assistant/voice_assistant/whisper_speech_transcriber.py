"""Small adapter that normalizes Faster-Whisper transcription results."""

from typing import Iterable

import numpy as np
from faster_whisper import WhisperModel


class WhisperSpeechTranscriber:
    """Load one Whisper model and expose file and in-memory entry points."""

    def __init__(
        self,
        model_size: str = "base",
        language: str = "de",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        """Initialize the inference model.

        Args:
            model_size: Faster-Whisper model identifier, such as ``tiny``.
            language: Language code supplied to Whisper for decoding.
            device: Inference device accepted by Faster-Whisper.
            compute_type: Model quantization/precision mode.
        """
        self.model_size = model_size
        self.language = language
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )

    def transcribe(self, wav_path: str) -> str:
        """Transcribe an audio file and return normalized plain text."""
        segments, _info = self.model.transcribe(
            wav_path,
            language=self.language,
            vad_filter=True,
        )
        return self._segments_to_text(segments)

    def transcribe_waveform(self, waveform_16khz_float: np.ndarray) -> str:
        """Transcribe a mono 16 kHz float waveform held in memory."""
        segments, _info = self.model.transcribe(
            waveform_16khz_float.astype(np.float32),
            language=self.language,
            vad_filter=True,
        )
        return self._segments_to_text(segments)

    def _segments_to_text(self, segments: Iterable) -> str:
        """Join non-empty, lazily generated Whisper segments in order."""
        text_parts = [segment.text.strip() for segment in segments]
        return " ".join(part for part in text_parts if part)

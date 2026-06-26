# src/voice_assistant/voice_assistant/whisper_speech_transcriber.py

import numpy as np
from faster_whisper import WhisperModel


class WhisperSpeechTranscriber:
    def __init__(
        self,
        model_size: str = "base",
        language: str = "de",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self.model_size = model_size
        self.language = language
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )

    def transcribe(self, wav_path: str) -> str:
        segments, _info = self.model.transcribe(
            wav_path,
            language=self.language,
            vad_filter=True,
        )
        return self._segments_to_text(segments)

    def transcribe_waveform(
        self,
        waveform_16khz_float: np.ndarray,
    ) -> str:
        segments, _info = self.model.transcribe(
            waveform_16khz_float.astype(np.float32),
            language=self.language,
            vad_filter=True,
        )
        return self._segments_to_text(segments)

    def _segments_to_text(self, segments) -> str:
        text_parts = [segment.text.strip() for segment in segments]
        return " ".join(part for part in text_parts if part)
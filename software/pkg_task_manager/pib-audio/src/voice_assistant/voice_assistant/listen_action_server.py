import time
import wave
from collections import deque
from dataclasses import dataclass
from typing import Optional

import numpy as np
import rclpy
from datatypes.action import Listen
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node

from voice_assistant.yamnet_doorbell_classifier import YamnetDoorbellClassifier
from voice_assistant.whisper_speech_transcriber import WhisperSpeechTranscriber


class TerminalColor:
    RESET = "\033[0m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


FEEDBACK_MESSAGES = {
    "listening": ("Listening for doorbell...", TerminalColor.BLUE),
    "listening_for_speech": ("Preparing microphone for speech...", TerminalColor.BLUE),
    "ready_for_speech": ("Microphone ready. You can speak now.", TerminalColor.GREEN),
    "speech_detected": ("Speech detected. Keep speaking...", TerminalColor.YELLOW),
    "transcribing": ("Transcribing speech...", TerminalColor.CYAN),
    "speech_transcribed": ("Speech transcribed.", TerminalColor.GREEN),
    "no_speech_detected": ("No speech detected.", TerminalColor.RED),
    "no_transcript": ("Speech detected, but no transcript was created.", TerminalColor.RED),
    "doorbell_detected": ("Doorbell detected.", TerminalColor.GREEN),
    "timeout": ("Timeout. Nothing detected.", TerminalColor.RED),
    "cancelled": ("Listen goal cancelled.", TerminalColor.RED),
    "error": ("An error occurred.", TerminalColor.RED),
}


@dataclass
class DetectionState:
    detected: bool = False
    confidence: float = 0.0
    top_class: str = ""
    speech_score: float = 0.0


class ListenActionServer(Node):
    def __init__(self) -> None:
        super().__init__("voice_listen_action_server")

        self.declare_parameter("action_name", "/audio/listen")
        self.declare_parameter("doorbell_threshold", 0.30)
        self.declare_parameter("speech_threshold", 0.30)
        self.declare_parameter("speech_max_threshold", 0.25)

        self.declare_parameter("speech_model_size", "base")
        self.declare_parameter("speech_language", "de")
        self.declare_parameter("speech_device", "cpu")
        self.declare_parameter("speech_compute_type", "int8")

        self.declare_parameter("timeout_sec", 5.0)
        self.declare_parameter("wav_path", "")
        self.declare_parameter("sample_rate", 16000)
        self.declare_parameter("chunk_size", 16000)

        self.declare_parameter("speech_pre_roll_sec", 0.5)
        self.declare_parameter("speech_tail_sec", 1.2)
        self.declare_parameter("speech_max_segment_sec", 6.0)

        action_name = self.get_parameter("action_name").value

        self.get_logger().info("[ListenAction] Loading YAMNet model...")
        self.classifier = YamnetDoorbellClassifier(
            doorbell_threshold=float(self.get_parameter("doorbell_threshold").value),
            speech_max_threshold=float(self.get_parameter("speech_max_threshold").value),
        )

        self.get_logger().info("[ListenAction] Loading Whisper model...")
        self.speech_transcriber = WhisperSpeechTranscriber(
            model_size=str(self.get_parameter("speech_model_size").value),
            language=str(self.get_parameter("speech_language").value),
            device=str(self.get_parameter("speech_device").value),
            compute_type=str(self.get_parameter("speech_compute_type").value),
        )

        self._server = ActionServer(
            self,
            Listen,
            action_name,
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )

        self.get_logger().info(f"[ListenAction] Ready on {action_name}")

    def goal_callback(self, goal_request: Listen.Goal) -> GoalResponse:
        if goal_request.mode not in (
            Listen.Goal.MODE_DOORBELL,
            Listen.Goal.MODE_SPEECH,
        ):
            self.get_logger().warn(
                f"Rejecting listen goal: unknown mode={goal_request.mode}"
            )
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def cancel_callback(self, _goal_handle) -> CancelResponse:
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle) -> Listen.Result:
        default_timeout = float(self.get_parameter("timeout_sec").value)
        timeout_sec = float(goal_handle.request.timeout_sec or default_timeout)
        wav_path = str(self.get_parameter("wav_path").value or "")
        started_at = time.monotonic()
        mode = goal_handle.request.mode

        if mode == Listen.Goal.MODE_SPEECH:
            if wav_path:
                return self._execute_speech_from_wav(
                    goal_handle,
                    wav_path,
                    timeout_sec,
                    started_at,
                )

            return self._execute_speech_from_microphone(
                goal_handle,
                timeout_sec,
                started_at,
            )

        if wav_path:
            state = self._detect_audio_from_wav(
                wav_path,
                timeout_sec,
                goal_handle,
                started_at,
            )
        else:
            state = self._detect_doorbell_from_microphone(
                timeout_sec,
                goal_handle,
                started_at,
            )

        return self._finish_doorbell(goal_handle, state)

    def _execute_speech_from_wav(
        self,
        goal_handle,
        wav_path: str,
        timeout_sec: float,
        started_at: float,
    ) -> Listen.Result:
        result = Listen.Result()
        result.detected = False
        result.confidence = 0.0
        result.transcript = ""

        self._publish_feedback(goal_handle, "listening_for_speech")

        state = self._detect_audio_from_wav(
            wav_path,
            timeout_sec,
            goal_handle,
            started_at,
        )

        if goal_handle.is_cancel_requested:
            self._publish_feedback(goal_handle, "cancelled")
            goal_handle.canceled()
            return result

        result.confidence = float(state.speech_score)

        if not self._speech_was_detected(state):
            self._publish_feedback(goal_handle, "no_speech_detected")
            goal_handle.succeed()
            return result

        self._publish_feedback(goal_handle, "transcribing")

        try:
            transcript = self.speech_transcriber.transcribe(wav_path)
        except Exception as exc:
            self.get_logger().error(f"[ListenAction] Speech recognition failed: {exc}")
            self._publish_feedback(goal_handle, "error")
            goal_handle.succeed()
            return result

        result.transcript = transcript.strip()
        result.detected = bool(result.transcript)

        self._publish_feedback(
            goal_handle,
            "speech_transcribed" if result.detected else "no_transcript",
        )
        goal_handle.succeed()

        self.get_logger().info(
            f"[ListenAction] Speech result: "
            f"detected={result.detected}, "
            f"confidence={result.confidence:.3f}, "
            f"transcript='{result.transcript}'"
        )

        return result

    def _execute_speech_from_microphone(
        self,
        goal_handle,
        timeout_sec: float,
        started_at: float,
    ) -> Listen.Result:
        result = Listen.Result()
        result.detected = False
        result.confidence = 0.0
        result.transcript = ""

        self._publish_feedback(goal_handle, "listening_for_speech")

        speech_segment, state = self._capture_speech_segment_from_microphone(
            timeout_sec,
            goal_handle,
            started_at,
        )

        if goal_handle.is_cancel_requested:
            self._publish_feedback(goal_handle, "cancelled")
            goal_handle.canceled()
            return result

        result.confidence = float(state.speech_score)

        if speech_segment.size == 0:
            self._publish_feedback(goal_handle, "no_speech_detected")
            goal_handle.succeed()
            return result

        self._publish_feedback(goal_handle, "transcribing")

        try:
            transcript = self.speech_transcriber.transcribe_waveform(speech_segment)
        except Exception as exc:
            self.get_logger().error(f"[ListenAction] Speech recognition failed: {exc}")
            self._publish_feedback(goal_handle, "error")
            goal_handle.succeed()
            return result

        result.transcript = transcript.strip()
        result.detected = bool(result.transcript)

        self._publish_feedback(
            goal_handle,
            "speech_transcribed" if result.detected else "no_transcript",
        )
        goal_handle.succeed()

        self.get_logger().info(
            f"[ListenAction] Speech result: "
            f"detected={result.detected}, "
            f"confidence={result.confidence:.3f}, "
            f"transcript='{result.transcript}'"
        )

        return result

    def _capture_speech_segment_from_microphone(
        self,
        timeout_sec: float,
        goal_handle,
        started_at: float,
    ) -> tuple[np.ndarray, DetectionState]:
        state = DetectionState()

        try:
            import pyaudio
        except ImportError:
            self.get_logger().error("pyaudio is required for microphone listening")
            return np.array([], dtype=np.float32), state

        sample_rate = int(self.get_parameter("sample_rate").value)
        chunk_size = int(self.get_parameter("chunk_size").value)

        speech_pre_roll_sec = float(self.get_parameter("speech_pre_roll_sec").value)
        speech_tail_sec = float(self.get_parameter("speech_tail_sec").value)
        speech_max_segment_sec = float(
            self.get_parameter("speech_max_segment_sec").value
        )

        chunk_duration_sec = chunk_size / 16000.0
        pre_roll_chunks = max(1, int(speech_pre_roll_sec / chunk_duration_sec))

        pre_roll_buffer = deque(maxlen=pre_roll_chunks)
        speech_buffer: list[np.ndarray] = []

        speech_started = False
        speech_started_at: Optional[float] = None
        last_speech_at: Optional[float] = None

        audio = pyaudio.PyAudio()
        stream: Optional[object] = None

        try:
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk_size,
            )

            self._publish_feedback(goal_handle, "ready_for_speech")

            while True:
                now = time.monotonic()

                if goal_handle.is_cancel_requested:
                    return np.array([], dtype=np.float32), state

                if now - started_at >= timeout_sec:
                    break

                raw = stream.read(chunk_size, exception_on_overflow=False)
                waveform = self._pcm_to_float_mono(
                    raw,
                    sample_width=2,
                    channels=1,
                )
                waveform = self._resample_to_16khz(waveform, sample_rate)

                if waveform.size == 0:
                    continue

                classification = self.classifier.classify(waveform)
                self._update_state_from_classification(state, classification)

                current_chunk_is_speech = self._speech_was_detected(state)

                if not speech_started:
                    pre_roll_buffer.append(waveform)

                    if current_chunk_is_speech:
                        speech_started = True
                        speech_started_at = now
                        last_speech_at = now

                        speech_buffer.extend(list(pre_roll_buffer))
                        pre_roll_buffer.clear()

                        self._publish_feedback(goal_handle, "speech_detected")

                    continue

                speech_buffer.append(waveform)

                if current_chunk_is_speech:
                    last_speech_at = now

                segment_duration = (
                    now - speech_started_at
                    if speech_started_at is not None
                    else 0.0
                )

                silence_after_speech = (
                    last_speech_at is not None
                    and now - last_speech_at >= speech_tail_sec
                )
                segment_too_long = segment_duration >= speech_max_segment_sec

                if silence_after_speech or segment_too_long:
                    break

            if not speech_buffer:
                return np.array([], dtype=np.float32), state

            segment = np.concatenate(speech_buffer).astype(np.float32)

            self.get_logger().info(
                f"[ListenAction] Speech segment ready: "
                f"duration={segment.size / 16000.0:.2f}s, "
                f"speech_score={state.speech_score:.3f}, "
                f"top_class={state.top_class}"
            )

            return segment, state

        except Exception as exc:
            self.get_logger().error(f"Microphone speech listen failed: {exc}")
            return np.array([], dtype=np.float32), state

        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()
            audio.terminate()

    def _detect_audio_from_wav(
        self,
        wav_path: str,
        timeout_sec: float,
        goal_handle,
        started_at: float,
    ) -> DetectionState:
        state = DetectionState()

        try:
            with wave.open(wav_path, "rb") as wav:
                sample_rate = wav.getframerate()
                channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                frames_per_chunk = int(self.get_parameter("chunk_size").value)

                while True:
                    if goal_handle.is_cancel_requested:
                        return state

                    if time.monotonic() - started_at >= timeout_sec:
                        return state

                    raw = wav.readframes(frames_per_chunk)

                    if not raw:
                        return state

                    waveform = self._pcm_to_float_mono(
                        raw,
                        sample_width,
                        channels,
                    )
                    waveform = self._resample_to_16khz(waveform, sample_rate)

                    if waveform.size == 0:
                        continue

                    classification = self.classifier.classify(waveform)
                    self._update_state_from_classification(state, classification)

                    doorbell_detected = bool(
                        classification.get(
                            "doorbell_detected",
                            classification.get("detected", False),
                        )
                    )

                    if doorbell_detected or self._speech_was_detected(state):
                        state.detected = doorbell_detected
                        return state

                    time.sleep(frames_per_chunk / max(sample_rate, 1))

        except Exception as exc:
            self.get_logger().error(f"Could not analyse wav_path={wav_path}: {exc}")

        return state

    def _detect_doorbell_from_microphone(
        self,
        timeout_sec: float,
        goal_handle,
        started_at: float,
    ) -> DetectionState:
        state = DetectionState()

        try:
            import pyaudio
        except ImportError:
            self.get_logger().error("pyaudio is required for microphone listening")
            return state

        sample_rate = int(self.get_parameter("sample_rate").value)
        chunk_size = int(self.get_parameter("chunk_size").value)

        audio = pyaudio.PyAudio()
        stream: Optional[object] = None

        try:
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk_size,
            )

            while True:
                if goal_handle.is_cancel_requested:
                    return state

                if time.monotonic() - started_at >= timeout_sec:
                    return state

                raw = stream.read(chunk_size, exception_on_overflow=False)
                waveform = self._pcm_to_float_mono(
                    raw,
                    sample_width=2,
                    channels=1,
                )
                waveform = self._resample_to_16khz(waveform, sample_rate)

                if waveform.size == 0:
                    continue

                classification = self.classifier.classify(waveform)
                self._update_state_from_classification(state, classification)

                doorbell_detected = bool(
                    classification.get(
                        "doorbell_detected",
                        classification.get("detected", False),
                    )
                )

                if doorbell_detected:
                    state.detected = True
                    return state

        except Exception as exc:
            self.get_logger().error(f"Microphone listen failed: {exc}")

        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()
            audio.terminate()

        return state

    def _finish_doorbell(
        self,
        goal_handle,
        state: DetectionState,
    ) -> Listen.Result:
        result = Listen.Result()
        result.detected = state.detected
        result.confidence = float(state.confidence)
        result.transcript = ""

        if goal_handle.is_cancel_requested:
            self._publish_feedback(goal_handle, "cancelled")
            goal_handle.canceled()
            return result

        if state.detected:
            self._publish_feedback(goal_handle, "doorbell_detected")
        else:
            self._publish_feedback(goal_handle, "timeout")

        goal_handle.succeed()

        self.get_logger().info(
            f"[ListenAction] Finished: "
            f"detected={result.detected} "
            f"confidence={result.confidence:.3f} "
            f"top_class={state.top_class} "
            f"speech_score={state.speech_score:.3f}"
        )

        return result

    def _speech_was_detected(self, state: DetectionState) -> bool:
        speech_threshold = float(self.get_parameter("speech_threshold").value)
        return state.speech_score >= speech_threshold

    def _update_state_from_classification(
        self,
        state: DetectionState,
        classification: dict,
    ) -> None:
        doorbell_score = float(classification["doorbell_score"])
        speech_score = float(classification["speech_score"])
        top_class = str(classification["top_class"])

        state.confidence = max(state.confidence, doorbell_score, speech_score)
        state.speech_score = max(state.speech_score, speech_score)
        state.top_class = top_class

        self.get_logger().info(
            f"[ListenAction] YAMNet: "
            f"doorbell_score={doorbell_score:.3f} "
            f"speech_score={speech_score:.3f} "
            f"top_class={top_class}"
        )

    def _pcm_to_float_mono(
        self,
        raw: bytes,
        sample_width: int,
        channels: int,
    ) -> np.ndarray:
        if sample_width != 2:
            self.get_logger().warn(
                "Only 16-bit PCM audio is supported for YAMNet detection"
            )
            return np.array([], dtype=np.float32)

        samples = np.frombuffer(raw, dtype=np.int16)

        if samples.size == 0:
            return np.array([], dtype=np.float32)

        if channels > 1:
            samples = samples.reshape(-1, channels).mean(axis=1)

        return samples.astype(np.float32) / 32768.0

    def _resample_to_16khz(
        self,
        waveform: np.ndarray,
        source_sample_rate: int,
    ) -> np.ndarray:
        target_sample_rate = 16000

        if waveform.size == 0:
            return np.array([], dtype=np.float32)

        if source_sample_rate == target_sample_rate:
            return waveform.astype(np.float32)

        duration = waveform.size / float(source_sample_rate)
        target_size = int(duration * target_sample_rate)

        if target_size <= 0:
            return np.array([], dtype=np.float32)

        old_positions = np.linspace(
            0.0,
            duration,
            num=waveform.size,
            endpoint=False,
        )
        new_positions = np.linspace(
            0.0,
            duration,
            num=target_size,
            endpoint=False,
        )

        return np.interp(new_positions, old_positions, waveform).astype(np.float32)

    def _publish_feedback(self, goal_handle, state: str) -> None:
        feedback = Listen.Feedback()
        feedback.state = state
        goal_handle.publish_feedback(feedback)

        message, color = FEEDBACK_MESSAGES.get(
            state,
            (f"State: {state}", TerminalColor.RESET),
        )

        self.get_logger().info(
            f"{color}[ListenAction] {message}{TerminalColor.RESET}"
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ListenActionServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
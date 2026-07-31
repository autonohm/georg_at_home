# PIB Audio Voice Assistant

This repository contains a ROS 2 voice-assistant prototype for detecting
doorbells and transcribing speech. It supports live microphone input,
pre-recorded WAV files, and ROS bag audio streams.

The project uses:

- [YAMNet](https://tfhub.dev/google/yamnet/1) for doorbell and speech
  classification
- [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) for speech
  transcription
- ROS 2 actions for cancellable listening requests
- ROS 2 messages for the event-to-task demonstration pipeline

## Repository structure

```text
.
├── README.md
└── src
    ├── datatypes
    │   ├── action/Listen.action
    │   └── msg
    │       ├── VoiceEvent.msg
    │       └── VoiceTask.msg
    └── voice_assistant
        ├── launch
        ├── voice_assistant
        ├── boot_scripts
        ├── package.xml
        └── setup.py
```

`datatypes` is an `ament_cmake` interface package. `voice_assistant` is an
`ament_python` package containing the ROS nodes, launch files, classifiers,
and transcription adapter.

## Architecture

The repository provides two related processing paths.

### Listen action

```text
DoorbellTaskManagerDemo ─┐
                        ├── /audio/listen ──> ListenActionServer
SpeechTaskManagerDemo ──┘                         │
                                                 ├── YAMNet classification
                                                 └── Faster-Whisper transcription
```

The `ListenActionServer` accepts doorbell and speech goals. Audio comes from
the system microphone unless the server's `wav_path` parameter is set.

### Event-to-task demonstration

```text
Audio detector
      │
      ▼
/voice/events (VoiceEvent)
      │
      ▼
VoiceRuleEngine
      │
      ▼
/voice/tasks (VoiceTask)
      │
      ▼
VoiceTaskDispatcher
```

The current dispatcher logs the task that would be submitted to a downstream
task-management system.

## ROS interfaces

### `Listen` action

Action name: `/audio/listen` by default.

Goal:

- `mode`: `MODE_DOORBELL` (`1`) or `MODE_SPEECH` (`2`)
- `timeout_sec`: Goal-specific timeout; `0` selects the server default

Result:

- `detected`: Whether a doorbell or a non-empty speech transcript was detected
- `confidence`: Highest relevant YAMNet score
- `transcript`: Recognized text in speech mode; empty in doorbell mode

Feedback states include `listening_for_speech`, `ready_for_speech`,
`speech_detected`, `transcribing`, `speech_transcribed`,
`no_speech_detected`, `doorbell_detected`, `timeout`, `cancelled`, and
`error`.

### Topics

| Topic | Type | Purpose |
| --- | --- | --- |
| `/audio_stream` | `std_msgs/Int16MultiArray` | Signed 16-bit PCM chunks for the threshold detector |
| `/voice/events` | `datatypes/VoiceEvent` | Structured detector output |
| `/voice/tasks` | `datatypes/VoiceTask` | Tasks generated from voice events |

The topic names are fixed except for the threshold detector's configurable
audio input topic.

## Requirements

- ROS 2 Humble
- Python 3
- A working microphone and PortAudio/PyAudio for live input
- TensorFlow and TensorFlow Hub for YAMNet
- Faster-Whisper for transcription
- NumPy

On Debian or Ubuntu, the native audio and media dependencies can be installed
with:

```bash
sudo apt update
sudo apt install portaudio19-dev libsndfile1 ffmpeg python3-pip
```

Install the Python runtime dependencies in the environment used by ROS:

```bash
python3 -m pip install \
  numpy \
  pyaudio \
  tensorflow \
  tensorflow-hub \
  faster-whisper
```

The first run may download the YAMNet and Whisper model files. It therefore
requires network access and can take longer than subsequent starts.

## Build

Run the following commands from the repository root:

```bash
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

To rebuild only these packages:

```bash
colcon build --packages-select datatypes voice_assistant
source install/setup.bash
```

Source `install/setup.bash` in every new terminal before running a node or
launch file.

## Usage

### Doorbell action with a WAV file

The WAV detector expects signed 16-bit PCM. Audio is converted to mono and
resampled to 16 kHz before YAMNet inference.

```bash
ros2 launch voice_assistant demo_listen_action_doorbell.launch.py \
  wav_path:=/absolute/path/to/doorbell.wav \
  timeout_sec:=30.0 \
  repeat:=false
```

Omit `wav_path` to capture from the default system microphone:

```bash
ros2 launch voice_assistant demo_listen_action_doorbell.launch.py \
  timeout_sec:=30.0
```

### Speech action

Use a WAV file for deterministic transcription:

```bash
ros2 launch voice_assistant demo_listen_action_speech.launch.py \
  wav_path:=/absolute/path/to/speech.wav \
  speech_model_size:=tiny \
  speech_language:=de
```

Use the microphone by leaving `wav_path` empty:

```bash
ros2 launch voice_assistant demo_listen_action_speech.launch.py \
  timeout_sec:=10.0 \
  speech_language:=de
```

The microphone path retains a short pre-roll before detected speech, records
until trailing silence is observed, and then sends the captured segment to
Whisper.

### One-shot YAMNet WAV pipeline

This launch file runs the WAV detector, rule engine, and task dispatcher:

```bash
ros2 launch voice_assistant demo_doorbell_wav.launch.py \
  wav_path:=/absolute/path/to/doorbell.wav
```

### Threshold detector with a ROS bag

The bag must publish signed 16-bit samples as
`std_msgs/msg/Int16MultiArray`:

```bash
ros2 launch voice_assistant demo_doorbell_bag.launch.py \
  bag_path:=/absolute/path/to/bag \
  audio_topic:=/audio_stream \
  threshold:=1000
```

This detector uses RMS amplitude only. It is intended for lightweight
integration demonstrations rather than semantic sound classification.

## Configuration

### Listen action server

| Parameter | Default | Description |
| --- | ---: | --- |
| `action_name` | `/audio/listen` | ROS action endpoint |
| `doorbell_threshold` | `0.30` | Minimum YAMNet doorbell score |
| `speech_threshold` | `0.30` | Minimum YAMNet speech score |
| `speech_max_threshold` | `0.25` | Maximum speech score allowed for a doorbell result |
| `speech_model_size` | `base` | Faster-Whisper model identifier |
| `speech_language` | `de` | Whisper decoding language |
| `speech_device` | `cpu` | Whisper inference device |
| `speech_compute_type` | `int8` | Whisper compute/quantization mode |
| `timeout_sec` | `5.0` | Default goal timeout |
| `wav_path` | empty | WAV input; empty selects the microphone |
| `sample_rate` | `16000` | Microphone sample rate |
| `chunk_size` | `16000` | Frames read and classified per chunk |
| `speech_pre_roll_sec` | `0.5` | Audio retained before detected speech |
| `speech_tail_sec` | `1.2` | Silence required to end speech capture |
| `speech_max_segment_sec` | `6.0` | Maximum captured utterance duration |

### Threshold stream detector

| Parameter | Default | Description |
| --- | ---: | --- |
| `audio_topic` | `/audio_stream` | PCM input topic |
| `threshold` | `1000` | Minimum RMS amplitude |
| `cooldown_chunks` | `20` | Chunks ignored after a published event |

## Running individual nodes

After building and sourcing the workspace, nodes can also be started directly:

```bash
ros2 run voice_assistant listen_action_server
ros2 run voice_assistant doorbell_task_manager_demo
ros2 run voice_assistant speech_task_manager_demo
ros2 run voice_assistant doorbell_wav_detector
ros2 run voice_assistant doorbell_audio_stream_detector
ros2 run voice_assistant demo_doorbell_detector
ros2 run voice_assistant voice_rule_engine
ros2 run voice_assistant voice_task_dispatcher
```

ROS parameters can be passed with the standard `--ros-args -p` syntax:

```bash
ros2 run voice_assistant listen_action_server --ros-args \
  -p speech_language:=en \
  -p speech_model_size:=small \
  -p timeout_sec:=15.0
```

## Development checks

Compile all Python files without starting ROS:

```bash
python3 -m compileall -q \
  src/voice_assistant/launch \
  src/voice_assistant/voice_assistant
```

Run package tests after building:

```bash
colcon test --packages-select datatypes voice_assistant
colcon test-result --verbose
```

## Current limitations

- The event-to-task dispatcher is a demonstration and only logs tasks.
- The threshold stream detector treats any sufficiently loud chunk as a
  doorbell candidate.
- Live capture uses the default single-channel PyAudio input device.
- The WAV loaders support signed 16-bit PCM for classifier input.
- The systemd boot script references `launch.py`, which is not present in the
  current package. Use one of the documented launch files or update the service
  for the intended deployment.
- Package metadata still contains placeholder description, maintainer, and
  license values. No license should be inferred until those fields are updated.

# pib-audio

Audio and voice package for the pib robot "Georg". It contains:

- **`datatypes`**: ROS 2 message and action definitions for audio events and listening (`Listen.action`, `VoiceEvent.msg`, `VoiceTask.msg`).
- **`voice_assistant`**: ROS 2 nodes that detect a doorbell with YAMNet, transcribe speech with Whisper, and expose both as the `Listen` action.

The Task Manager uses the `Listen` action through the `Listening` task (`georg_task_manager/georg_task_manager/tasks/Listening.py`).

## Package layout

```
pib-audio/
├── requirements.txt              # Python dependencies (TensorFlow, faster-whisper, PyAudio, ...)
├── requirements.lock.txt         # pinned versions
└── src/
    ├── datatypes/                # ament_cmake: messages and actions
    │   ├── action/Listen.action
    │   └── msg/VoiceEvent.msg, VoiceTask.msg
    └── voice_assistant/          # ament_python: nodes
        ├── voice_assistant/
        │   ├── listen_action_server.py          # Listen action server (main node)
        │   ├── yamnet_doorbell_classifier.py    # YAMNet classification (doorbell / speech scores)
        │   ├── whisper_speech_transcriber.py    # faster-whisper transcription
        │   ├── speech_task_manager_demo.py      # demo client for speech
        │   ├── doorbell_task_manager_demo.py    # demo client for doorbell
        │   ├── voice_rule_engine.py, voice_task_dispatcher.py, doorbell_*.py
        ├── launch/                   # demo launch files
        ├── boot_scripts/             # systemd service and start script for the robot
        ├── Dockerfile
        └── requirements.txt
```

## Action interface

`src/datatypes/action/Listen.action`:

```
# Goal
uint8 MODE_DOORBELL=1
uint8 MODE_SPEECH=2

uint8 mode
float32 timeout_sec
---
# Result
bool detected
float32 confidence
string transcript
---
# Feedback
string state
```

| Field | Meaning |
|---|---|
| `mode` | `MODE_DOORBELL` waits for a doorbell sound. `MODE_SPEECH` records a speech segment and transcribes it. Other values are rejected. |
| `timeout_sec` | Maximum listen time. `0` uses the server parameter `timeout_sec`. |
| `detected` | `true` if a doorbell (or, in speech mode, a non-empty transcript) was found. |
| `confidence` | Highest doorbell score (doorbell mode) or speech score (speech mode). |
| `transcript` | Recognized text (speech mode only). |
| `state` (feedback) | Progress string, e.g. `listening`, `speech_detected`, `transcribing`, `doorbell_detected`, `timeout`. |

The action name defaults to `/audio/listen` (parameter `action_name`).

## Build

The `datatypes` package must be built before `voice_assistant`. The Docker image runs `colcon build` for the whole workspace. To build by hand:

```bash
colcon build --packages-select datatypes voice_assistant
source install/setup.bash
```

Install the Python dependencies in the environment the node runs in:

```bash
pip install -r pib-audio/requirements.txt
```

`PyAudio` needs `portaudio19-dev` installed on the system.

## Running the listen server

```bash
source install/setup.bash
ros2 run voice_assistant listen_action_server
```

The node is named `voice_listen_action_server` when started through the launch file, and `listen_action_server` when started with `ros2 run`. The Task Manager launch file currently has this node commented out (`#voice_module`), so start it separately if you need it.

### Parameters

| Parameter | Default | Purpose |
|---|---|---|
| `action_name` | `/audio/listen` | Action name |
| `doorbell_threshold` | `0.30` | Minimum doorbell score |
| `speech_threshold` | `0.30` | Minimum speech score |
| `speech_max_threshold` | `0.25` | Used by the YAMNet classifier |
| `speech_model_size` | `base` | Whisper model (`tiny`, `base`, ...) |
| `speech_language` | `de` | Whisper language |
| `speech_device` | `cpu` | Whisper device |
| `speech_compute_type` | `int8` | Whisper compute type |
| `timeout_sec` | `5.0` | Default listen time |
| `wav_path` | `""` | If set, analyze this WAV file instead of the microphone (useful for tests) |
| `sample_rate` | `16000` | Microphone sample rate |
| `chunk_size` | `16000` | Samples per chunk |
| `speech_pre_roll_sec` | `0.5` | Audio kept before speech starts |
| `speech_tail_sec` | `1.2` | Silence that ends a speech segment |
| `speech_max_segment_sec` | `6.0` | Maximum speech segment length |

Example launch with overrides:

```bash
ros2 launch voice_assistant demo_listen_action_speech.launch.py \
  speech_model_size:=tiny timeout_sec:=10.0
```

### Testing without a microphone

Pass a WAV file to the server with the `wav_path` parameter. The server analyzes the file instead of recording:

```bash
ros2 launch voice_assistant demo_listen_action_doorbell.launch.py wav_path:=/path/to/doorbell.wav
```

Other launch files: `demo_doorbell_wav.launch.py`, `demo_doorbell_bag.launch.py`, `demo_listen_action_speech.launch.py`.

## Using the action from the Task Manager

The Task Manager creates the client in `georg_task_manager/georg_task_manager/Georg.py`:

```python
self.listen_action_client = ActionClient(node, Listen, "audio/listen")
```

and `tasks/Listening.py` builds the goal:

```python
goal_msg = Listen.Goal()
goal_msg.mode = Listen.Goal.MODE_SPEECH   # or MODE_DOORBELL
goal_msg.timeout_sec = self.timeout_sec
```

In a mission:

```python
Listening("DOORBELL", 5.0, CRITICAL)
Listening("SPEECH")
```

## How to add a new listen mode or action

### A new mode for `Listen`

1. Add a constant to `src/datatypes/action/Listen.action`, e.g. `uint8 MODE_KEYWORD=3`.
2. Rebuild `datatypes` and re-source the workspace.
3. In `listen_action_server.py`:
   - accept the mode in `goal_callback`,
   - add a branch in `execute_callback` that calls a new `_execute_keyword(...)` method, following the pattern of `_execute_speech_from_microphone`,
   - publish feedback with `_publish_feedback` and add messages to `FEEDBACK_MESSAGES`.
4. In `georg_task_manager/tasks/Listening.py`, map the new sound name to the new mode.

### A completely new action

1. Create `src/datatypes/action/MyAction.action` and add it to `rosidl_generate_interfaces` in `src/datatypes/CMakeLists.txt`.
2. Create a server node in `src/voice_assistant/voice_assistant/`, following `listen_action_server.py`: an `ActionServer` with `goal_callback`, `cancel_callback`, and `execute_callback`, and a `main()` function.
3. Register it in `src/voice_assistant/setup.py` under `console_scripts`.
4. Add a `Node(...)` entry to a launch file in `launch/`.
5. Add a task in `georg_task_manager/georg_task_manager/tasks/` and a client in `Georg.py`.

## Known issues

- **Namespace mismatch risk.** The listen server defaults to the absolute action name `/audio/listen`, while the Task Manager client uses the relative name `audio/listen`. When everything is launched under the robot namespace (`georg`), an absolute name is not namespaced, and the two sides may not find each other. Pass `-p action_name:=audio/listen` to the server to match the client.
- **Node disabled in the Task Manager launch.** `voice_module` is commented out in `pkg_task_manager/config/task_manager.launch.py`, so `Listening` tasks will not get a server when the whole system is launched.
- **Dependencies differ.** `voice_assistant/package.xml` lists `openai`, `google-cloud-*`, and `SpeechRecognition`, but the code uses YAMNet (TensorFlow) and faster-whisper, which are in `requirements.txt`. Keep `package.xml` and `requirements.txt` in sync.

## Troubleshooting

- **`pyaudio is required for microphone listening`:** install `PyAudio` and `portaudio19-dev`, or use `wav_path` for tests.
- **`Only 16-bit PCM audio is supported`:** the WAV file must be 16-bit PCM.
- **Goal rejected:** the `mode` value is not `MODE_DOORBELL` or `MODE_SPEECH`.
- **Long startup:** the YAMNet and Whisper models are loaded when the node starts, not on the first goal.

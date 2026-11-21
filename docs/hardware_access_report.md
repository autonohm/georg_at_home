# Hardware-Zugriffs-Bericht (P7)

Erzeugt am 2026-11-21 von `tools/hardware_scan.py`. 3218 Dateien einzeln geprüft, 86 Fundstellen.

**Profil `real`: NICHT freigegeben** – es gibt offene Probleme (unten). Funde in fremden Paketen werden gemeldet, nicht umgebaut.

| Bewertung | Anzahl |
| --- | --- |
| Problem | 13 |
| offen | 8 |
| Hinweis | 56 |
| erlaubt | 9 |

## Meldungen an die Paket-Verantwortlichen

- **docker_base_image** (offen): beim Bauen geklonter Code, nicht im Repo geprüft. Stellen: `packages/docker_base_image/Dockerfile:9`
- **pkg_drive** (offen): Treiber-Code (edu_robot) wird beim Bauen geklont, nicht im Repo geprüft; muss cmd_vel/gated abonnieren. Stellen: `packages/pkg_drive/Dockerfile:23`, `packages/pkg_drive/Dockerfile:24`
- **pkg_examples** (Problem): privileged/Geräte-Zugriff außerhalb eines Treiber-Pakets; nicht nötig, entfernen. Stellen: `packages/pkg_examples/docker-compose.yaml:12`
- **pkg_gestures** (Problem): Aufruf heute auskommentiert (inaktiv); vor dem Aktivieren über ROS-Topics hinter dem Gate führen. Stellen: `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core/greet_person.py:16`, `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core/look_at.py:16`, `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core/point_to.py:16`, `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/utils/pib_control.py:12`, `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/utils/pib_control.py:13`
- **pkg_gestures** (Problem): pib-sdk steuert die Servos des pib direkt (über rosbridge/roslibpy), am command_gate vorbei. Stellen: `packages/pkg_gestures/Dockerfile:15`, `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/pyproject.toml:18`
- **pkg_slam** (Problem): SLAM braucht weder privileged noch /dev (Lidar über Netzwerk); entfernen. Stellen: `packages/pkg_slam/docker-compose.yaml:11`, `packages/pkg_slam/docker-compose.yaml:13`
- **pkg_slam** (offen): Sensor-Treiber (sick_scan_xd, rf2o, scan merger) werden geklont; lesend, nicht im Repo geprüft. Stellen: `packages/pkg_slam/Dockerfile:15`, `packages/pkg_slam/Dockerfile:16`, `packages/pkg_slam/Dockerfile:17`
- **pkg_urdf** (Problem): privileged/Geräte-Zugriff außerhalb eines Treiber-Pakets; nicht nötig, entfernen. Stellen: `packages/pkg_urdf/docker-compose.yaml:10`
- **pkg_urdf** (offen): beim Bauen geklonter Code, nicht im Repo geprüft. Stellen: `packages/pkg_urdf/Dockerfile:16`
- **pkg_viz** (Problem): RViz-Container (nur Profil viz) braucht kein /dev und kein privileged außer für die GPU; einschränken. Stellen: `packages/pkg_viz/docker-compose.yaml:11`, `packages/pkg_viz/docker-compose.yaml:23`
- **pkg_viz** (offen): beim Bauen geklonter Code, nicht im Repo geprüft. Stellen: `packages/pkg_viz/Dockerfile:26`

## Alle Fundstellen

| Paket | Datei | Zeile | Fundstelle | Regel | Bewertung | Begründung |
| --- | --- | --- | --- | --- | --- | --- |
| pkg_examples | `packages/pkg_examples/docker-compose.yaml` | 12 | `privileged: true` | privileged | Problem | privileged/Geräte-Zugriff außerhalb eines Treiber-Pakets; nicht nötig, entfernen |
| pkg_gestures | `packages/pkg_gestures/Dockerfile` | 15 | `pib-sdk==0.9.1` | controller sdk | Problem | pib-sdk steuert die Servos des pib direkt (über rosbridge/roslibpy), am command_gate vorbei |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/pyproject.toml` | 18 | `"pib-sdk"` | controller sdk | Problem | pib-sdk steuert die Servos des pib direkt (über rosbridge/roslibpy), am command_gate vorbei |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core/greet_person.py` | 16 | `###from pib_sdk.control import *` | controller sdk | Problem | Aufruf heute auskommentiert (inaktiv); vor dem Aktivieren über ROS-Topics hinter dem Gate führen |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core/look_at.py` | 16 | `###from pib_sdk.control import *` | controller sdk | Problem | Aufruf heute auskommentiert (inaktiv); vor dem Aktivieren über ROS-Topics hinter dem Gate führen |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core/point_to.py` | 16 | `###from pib_sdk.control import *` | controller sdk | Problem | Aufruf heute auskommentiert (inaktiv); vor dem Aktivieren über ROS-Topics hinter dem Gate führen |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/utils/pib_control.py` | 12 | `###from pib_sdk.kinematics import fk, ik` | controller sdk | Problem | Aufruf heute auskommentiert (inaktiv); vor dem Aktivieren über ROS-Topics hinter dem Gate führen |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/utils/pib_control.py` | 13 | `###from pib_sdk.control import *` | controller sdk | Problem | Aufruf heute auskommentiert (inaktiv); vor dem Aktivieren über ROS-Topics hinter dem Gate führen |
| pkg_slam | `packages/pkg_slam/docker-compose.yaml` | 11 | `- /dev:/dev` | device mount | Problem | SLAM braucht weder privileged noch /dev (Lidar über Netzwerk); entfernen |
| pkg_slam | `packages/pkg_slam/docker-compose.yaml` | 13 | `privileged: true` | privileged | Problem | SLAM braucht weder privileged noch /dev (Lidar über Netzwerk); entfernen |
| pkg_urdf | `packages/pkg_urdf/docker-compose.yaml` | 10 | `privileged: true` | privileged | Problem | privileged/Geräte-Zugriff außerhalb eines Treiber-Pakets; nicht nötig, entfernen |
| pkg_viz | `packages/pkg_viz/docker-compose.yaml` | 11 | `- /dev:/dev # hwaccel hopefully` | device mount | Problem | RViz-Container (nur Profil viz) braucht kein /dev und kein privileged außer für die GPU; einschränken |
| pkg_viz | `packages/pkg_viz/docker-compose.yaml` | 23 | `privileged: true` | privileged | Problem | RViz-Container (nur Profil viz) braucht kein /dev und kein privileged außer für die GPU; einschränken |
| docker_base_image | `packages/docker_base_image/Dockerfile` | 9 | `RUN git clone https://github.com/autonohm/georg_interfaces` | external code | offen | beim Bauen geklonter Code, nicht im Repo geprüft |
| pkg_command_gate | `packages/pkg_command_gate/command_gate/command_gate/command_gate_node.py` | 24 | `self._pub = self.create_publisher(Twist, 'cmd_vel/gated', 10)` | cmd_vel publisher | erlaubt | Gate bzw. Simulator selbst |
| pkg_drive | `packages/pkg_drive/Dockerfile` | 23 | `RUN git clone https://github.com/EduArt-Robotik/edu_robot.git --branch hotfix/single_channel_motor_controller && \` | external code | offen | Treiber-Code (edu_robot) wird beim Bauen geklont, nicht im Repo geprüft; muss cmd_vel/gated abonnieren |
| pkg_drive | `packages/pkg_drive/Dockerfile` | 24 | `git clone https://github.com/EduArt-Robotik/edu_robot_control.git` | external code | offen | Treiber-Code (edu_robot) wird beim Bauen geklont, nicht im Repo geprüft; muss cmd_vel/gated abonnieren |
| pkg_drive | `packages/pkg_drive/config/drive.launch.py` | 64 | `{'dev': '/dev/georg_controller'}` | device file | erlaubt | Treiber-Paket, nur Profil real, hinter dem command_gate |
| pkg_drive | `packages/pkg_drive/docker-compose.yaml` | 11 | `- /dev:/dev` | device mount | erlaubt | Treiber-Paket, nur Profil real, hinter dem command_gate |
| pkg_drive | `packages/pkg_drive/docker-compose.yaml` | 13 | `privileged: true` | privileged | erlaubt | Treiber-Paket, nur Profil real, hinter dem command_gate |
| pkg_gestures | `packages/pkg_gestures/Dockerfile` | 11 | `# pib-sdk replaces the former broken git submodule modules/pib_sdk.` | controller sdk | Hinweis | nur Kommentar/Docstring |
| pkg_gestures | `packages/pkg_gestures/Dockerfile` | 12 | `# Note: all pib_sdk imports in pib_gestures are commented out at the moment.` | controller sdk | Hinweis | nur Kommentar/Docstring |
| pkg_gestures | `packages/pkg_gestures/README.md` | 13 | `'pib-sdk' is installed with pip in the 'Dockerfile'. It replaces the former git submodule 'modules/pib_sdk', which had n` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 1 | `# pib-sdk` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 18 | `pip install pib-sdk` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 23 | `from pib_sdk.kinematics import fk, ik` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 37 | `from pib_sdk.control import *` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 38 | `from pib_sdk.kinematics import ik, fk` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 82 | `pib-sdk is able to send speech commands to voice assistant ROS topic easily similar to movement` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 84 | `from pib_sdk.speech import speak` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 145 | `from pib_sdk.kinematics import ik, fk` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 151 | `from pib_sdk.control import Write, right_arm` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 170 | `- **ERROR: Could not find a version that satisfies the requirement mediapipe (from pib-sdk) (from versions: none)**` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md` | 173 | `- **roslibpy.core.RosTimeoutError: Failed to connect to ROS**` | controller sdk | Hinweis | nur Dokumentation |
| pkg_gestures | `packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/utils/pib_control.py` | 5 | `more detailed description on pibrocks github / pib-sdk / branch-978` | controller sdk | Hinweis | nur Kommentar/Docstring |
| pkg_navigation | `packages/pkg_navigation/drive_route_server_pkg/drive_route_server/drive_route_action_server.py` | 177 | `self._cmd_vel_pub = self.create_publisher(Twist, CMD_VEL_TOPIC, 10)` | cmd_vel publisher | Hinweis | Fahrbefehl über ROS (cmd_vel). Im Profil real per Launch auf cmd_vel/nav umgeleitet -> twist_mux -> twist_limiter -> command_gate |
| pkg_object_detection | `packages/pkg_object_detection/README.md` | 5 | `'''git clone --depth 1 https://github.com/luxonis/oak-examples.git` | external code | Hinweis | nur Dokumentation |
| pkg_slam | `packages/pkg_slam/Dockerfile` | 15 | `RUN git clone https://github.com/SICKAG/sick_scan_xd.git --branch 3.8.0 && \` | external code | offen | Sensor-Treiber (sick_scan_xd, rf2o, scan merger) werden geklont; lesend, nicht im Repo geprüft |
| pkg_slam | `packages/pkg_slam/Dockerfile` | 16 | `git clone https://github.com/MAPIRlab/rf2o_laser_odometry.git && \` | external code | offen | Sensor-Treiber (sick_scan_xd, rf2o, scan merger) werden geklont; lesend, nicht im Repo geprüft |
| pkg_slam | `packages/pkg_slam/Dockerfile` | 17 | `git clone https://github.com/BruceChanJianLe/laser_scan_merger.git` | external code | offen | Sensor-Treiber (sick_scan_xd, rf2o, scan merger) werden geklont; lesend, nicht im Repo geprüft |
| pkg_slam | `packages/pkg_slam/config/lidars.launch.py` | 28 | `arguments=[node_arguments, "hostname:=192.168.2.104", "frame_id:=laser1_frame", "tf_publish_rate:=0.0"],` | hardware ip | erlaubt | Netzwerk-Lidar (SICK), nur lesend, kein Aktor |
| pkg_slam | `packages/pkg_slam/config/lidars.launch.py` | 36 | `arguments=[node_arguments, "hostname:=192.168.2.144", "frame_id:=laser2_frame", "tf_publish_rate:=0.0"],` | hardware ip | erlaubt | Netzwerk-Lidar (SICK), nur lesend, kein Aktor |
| pkg_speech | `packages/pkg_speech/README.md` | 45 | `# - ALSA_CARD=ArrayUAC10 #  <-- remove this line` | audio device | Hinweis | nur Dokumentation |
| pkg_speech | `packages/pkg_speech/README.md` | 46 | `- PULSE_SERVER=unix:${XDG_RUNTIME_DIR:-/run/user/1000}/pulse/native` | audio device | Hinweis | nur Dokumentation |
| pkg_task_manager | `packages/pkg_task_manager/Dockerfile` | 24 | `PyAudio==0.2.14 \` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/Dockerfile` | 48 | `#RUN git clone https://github.com/Giusaurus/pkg_navigation.git` | external code | Hinweis | nur Kommentar/Docstring |
| pkg_task_manager | `packages/pkg_task_manager/docker-compose.yaml` | 31 | `devices:` | device mount | Hinweis | nur Audio-Geräte (/dev/snd) für die Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/docker-compose.yaml` | 32 | `- /dev/snd:/dev/snd` | device file | Hinweis | nur Audio-Geräte (/dev/snd) für die Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/docker-compose.yaml` | 32 | `- /dev/snd:/dev/snd` | device mount | Hinweis | nur Audio-Geräte (/dev/snd) für die Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/georg_task_manager/test/test_mcap_integration.py` | 77 | `cmd = client.node.create_publisher(Twist, f'{NS}/cmd_vel', 10)` | cmd_vel publisher | Hinweis | Fahrbefehl über ROS; läuft über das command_gate |
| pkg_task_manager | `packages/pkg_task_manager/georg_task_manager/test/test_sim_integration.py` | 75 | `self.cmd = node.create_publisher(Twist, f'{NS}/cmd_vel', 10)` | cmd_vel publisher | Hinweis | Fahrbefehl über ROS; läuft über das command_gate |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/README.md` | 14 | `├── requirements.txt              # Python dependencies (TensorFlow, faster-whisper, PyAudio, ...)` | audio device | Hinweis | nur Dokumentation |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/README.md` | 81 | `'PyAudio' needs 'portaudio19-dev' installed on the system.` | audio device | Hinweis | nur Dokumentation |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/README.md` | 180 | `- **'pyaudio is required for microphone listening':** install 'PyAudio' and 'portaudio19-dev', or use 'wav_path' for tes` | audio device | Hinweis | nur Dokumentation |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/requirements.lock.txt` | 77 | `PyAudio==0.2.14` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/requirements.txt` | 5 | `PyAudio==0.2.14` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/Dockerfile` | 15 | `libusb-1.0-0-dev \` | usb | Hinweis | USB-Bibliothek für das Mikrofon-Array der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/Dockerfile` | 24 | `pyaudio \` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/Dockerfile` | 48 | `ENV PULSE_SERVER=unix:"${XDG_RUNTIME_DIR}/pulse/native"` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/package.xml` | 16 | `<exec_depend>pyaudio</exec_depend>` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/requirements.txt` | 50 | `PyAudio==0.2.14` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/requirements.txt` | 68 | `pyaudio==0.2.14` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/listen_action_server.py` | 282 | `import pyaudio` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/listen_action_server.py` | 284 | `self.get_logger().error("pyaudio is required for microphone listening")` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/listen_action_server.py` | 306 | `audio = pyaudio.PyAudio()` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/listen_action_server.py` | 311 | `format=pyaudio.paInt16,` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/listen_action_server.py` | 472 | `import pyaudio` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/listen_action_server.py` | 474 | `self.get_logger().error("pyaudio is required for microphone listening")` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/listen_action_server.py` | 480 | `audio = pyaudio.PyAudio()` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_task_manager | `packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/listen_action_server.py` | 485 | `format=pyaudio.paInt16,` | audio device | Hinweis | Mikrofon/Lautsprecher der Spracherkennung, kein Bewegungsaktor |
| pkg_urdf | `packages/pkg_urdf/Dockerfile` | 16 | `RUN git clone https://github.com/autonohm/georg_description.git` | external code | offen | beim Bauen geklonter Code, nicht im Repo geprüft |
| pkg_viz | `packages/pkg_viz/Dockerfile` | 26 | `RUN git clone https://github.com/autonohm/georg_description.git` | external code | offen | beim Bauen geklonter Code, nicht im Repo geprüft |
| system-files | `system-files/README.md` | 16 | `git clone https://github.com/autonohm/georg_at_home.git` | external code | Hinweis | nur Dokumentation |
| system-files | `system-files/README.md` | 31 | `git clone https://github.com/autonohm/georg_at_home.git` | external code | Hinweis | nur Dokumentation |
| system-files | `system-files/etc/udev/rules.d/51-autonohm-joystick.rules` | 1 | `# PS3 Controller werden auf /dev/georg_controller erwartet` | device file | Hinweis | nur Kommentar/Docstring |
| system-files | `system-files/etc/udev/rules.d/51-autonohm-joystick.rules` | 2 | `KERNEL=="js?", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="0268", SYMLINK+="georg_controller", MODE="0666"` | udev rule | erlaubt | Joystick für die Fernsteuerung in pkg_drive (Treiber) |
| system-files | `system-files/etc/udev/rules.d/51-autonohm-joystick.rules` | 5 | `SUBSYSTEM=="input", ATTRS{idVendor}=="1017", ATTRS{idProduct}=="9015", ENV{ID_INPUT_JOYSTICK}=="?*", ENV{ID_INPUT_JOYSTI` | udev rule | erlaubt | Joystick für die Fernsteuerung in pkg_drive (Treiber) |
| system-files | `system-files/etc/udev/rules.d/51-autonohm-joystick.rules` | 6 | `SUBSYSTEM=="input", ATTRS{idVendor}=="1017", ATTRS{idProduct}=="9015", KERNEL=="js[0-9]*", RUN+="/bin/rm %E{DEVNAME}", E` | udev rule | erlaubt | Joystick für die Fernsteuerung in pkg_drive (Treiber) |
| system-files | `system-files/etc/udev/rules.d/99-pib-motors.rules` | 2 | `SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ATTRS{serial}=="5A7C122308", SYMLINK+="ttyMotor0"` | tty | Hinweis | Motor-Controller-Regel; im Repo nutzt sie kein Paket (vermutlich pib-backend auf dem Pi) |
| system-files | `system-files/etc/udev/rules.d/99-pib-motors.rules` | 2 | `SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ATTRS{serial}=="5A7C122308", SYMLINK+="ttyMotor0"` | udev rule | Hinweis | Motor-Controller-Regel; im Repo nutzt sie kein Paket (vermutlich pib-backend auf dem Pi) |
| system-files | `system-files/etc/udev/rules.d/99-pib-motors.rules` | 5 | `SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ATTRS{serial}=="5AE6083257", SYMLINK+="ttyMotor1"` | tty | Hinweis | Motor-Controller-Regel; im Repo nutzt sie kein Paket (vermutlich pib-backend auf dem Pi) |
| system-files | `system-files/etc/udev/rules.d/99-pib-motors.rules` | 5 | `SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ATTRS{serial}=="5AE6083257", SYMLINK+="ttyMotor1"` | udev rule | Hinweis | Motor-Controller-Regel; im Repo nutzt sie kein Paket (vermutlich pib-backend auf dem Pi) |
| system-files | `system-files/etc/udev/rules.d/99-pib-motors.rules` | 8 | `SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ATTRS{serial}=="58CD176727", SYMLINK+="ttyMotor2"` | tty | Hinweis | Motor-Controller-Regel; im Repo nutzt sie kein Paket (vermutlich pib-backend auf dem Pi) |
| system-files | `system-files/etc/udev/rules.d/99-pib-motors.rules` | 8 | `SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ATTRS{serial}=="58CD176727", SYMLINK+="ttyMotor2"` | udev rule | Hinweis | Motor-Controller-Regel; im Repo nutzt sie kein Paket (vermutlich pib-backend auf dem Pi) |
| system-files | `system-files/etc/udev/rules.d/99-pib-motors.rules` | 11 | `SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ATTRS{serial}=="5A7C121913", SYMLINK+="ttyMotor3"` | tty | Hinweis | Motor-Controller-Regel; im Repo nutzt sie kein Paket (vermutlich pib-backend auf dem Pi) |
| system-files | `system-files/etc/udev/rules.d/99-pib-motors.rules` | 11 | `SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ATTRS{serial}=="5A7C121913", SYMLINK+="ttyMotor3"` | udev rule | Hinweis | Motor-Controller-Regel; im Repo nutzt sie kein Paket (vermutlich pib-backend auf dem Pi) |

## Geprüfte Dateien (Beleg)

3218 Dateien, jede einzeln gelesen.

```
compose.yaml  –  26 Zeilen geprüft
packages/docker_base_image/Dockerfile  –  27 Zeilen geprüft
packages/docker_base_image/compose.yaml  –  11 Zeilen geprüft
packages/pkg_command_gate/Dockerfile  –  23 Zeilen geprüft
packages/pkg_command_gate/README.md  –  25 Zeilen geprüft
packages/pkg_command_gate/command_gate/command_gate/__init__.py  –  1 Zeilen geprüft
packages/pkg_command_gate/command_gate/command_gate/command_gate_node.py  –  63 Zeilen geprüft
packages/pkg_command_gate/command_gate/command_gate/gate.py  –  29 Zeilen geprüft
packages/pkg_command_gate/command_gate/package.xml  –  19 Zeilen geprüft
packages/pkg_command_gate/command_gate/resource/command_gate  –  1 Zeilen geprüft
packages/pkg_command_gate/command_gate/setup.cfg  –  5 Zeilen geprüft
packages/pkg_command_gate/command_gate/setup.py  –  26 Zeilen geprüft
packages/pkg_command_gate/command_gate/test/test_gate.py  –  27 Zeilen geprüft
packages/pkg_command_gate/config/command_gate.launch.py  –  26 Zeilen geprüft
packages/pkg_command_gate/docker-compose.yaml  –  24 Zeilen geprüft
packages/pkg_drive/Dockerfile  –  38 Zeilen geprüft
packages/pkg_drive/README.md  –  18 Zeilen geprüft
packages/pkg_drive/config/drive.launch.py  –  94 Zeilen geprüft
packages/pkg_drive/config/edu_robot.yaml  –  158 Zeilen geprüft
packages/pkg_drive/config/edu_robot_control.yaml  –  25 Zeilen geprüft
packages/pkg_drive/config/twist_limiter.yaml  –  23 Zeilen geprüft
packages/pkg_drive/config/twist_mux/joystick.yaml  –  12 Zeilen geprüft
packages/pkg_drive/config/twist_mux/twist_mux_launch.py  –  87 Zeilen geprüft
packages/pkg_drive/config/twist_mux/twist_mux_locks.yaml  –  27 Zeilen geprüft
packages/pkg_drive/config/twist_mux/twist_mux_topics.yaml  –  27 Zeilen geprüft
packages/pkg_drive/docker-compose.yaml  –  22 Zeilen geprüft
packages/pkg_drive/twist_limiter/.gitignore  –  7 Zeilen geprüft
packages/pkg_drive/twist_limiter/CMakeLists.txt  –  31 Zeilen geprüft
packages/pkg_drive/twist_limiter/LICENSE  –  18 Zeilen geprüft
packages/pkg_drive/twist_limiter/README.md  –  30 Zeilen geprüft
packages/pkg_drive/twist_limiter/package.xml  –  17 Zeilen geprüft
packages/pkg_drive/twist_limiter/src/dynamic_signal_generator.cpp  –  62 Zeilen geprüft
packages/pkg_drive/twist_limiter/src/main.cpp  –  107 Zeilen geprüft
packages/pkg_examples/Dockerfile  –  23 Zeilen geprüft
packages/pkg_examples/README.md  –  17 Zeilen geprüft
packages/pkg_examples/config/examples.launch.py  –  49 Zeilen geprüft
packages/pkg_examples/docker-compose.yaml  –  20 Zeilen geprüft
packages/pkg_examples/pib_action_template/CMakeLists.txt  –  24 Zeilen geprüft
packages/pkg_examples/pib_action_template/LICENSE  –  203 Zeilen geprüft
packages/pkg_examples/pib_action_template/README_demo.md  –  39 Zeilen geprüft
packages/pkg_examples/pib_action_template/README_template.md  –  117 Zeilen geprüft
packages/pkg_examples/pib_action_template/action/Template.action  –  6 Zeilen geprüft
packages/pkg_examples/pib_action_template/modules/__init__.py  –  1 Zeilen geprüft
packages/pkg_examples/pib_action_template/modules/action_demo_client.py  –  107 Zeilen geprüft
packages/pkg_examples/pib_action_template/modules/action_demo_server.py  –  119 Zeilen geprüft
packages/pkg_examples/pib_action_template/modules/action_template_client.py  –  91 Zeilen geprüft
packages/pkg_examples/pib_action_template/modules/action_template_server.py  –  102 Zeilen geprüft
packages/pkg_examples/pib_action_template/package.xml  –  26 Zeilen geprüft
packages/pkg_examples/pib_topic_template/LICENSE  –  203 Zeilen geprüft
packages/pkg_examples/pib_topic_template/README.md  –  108 Zeilen geprüft
packages/pkg_examples/pib_topic_template/modules/__init__.py  –  1 Zeilen geprüft
packages/pkg_examples/pib_topic_template/modules/topic_template_subscriber.py  –  45 Zeilen geprüft
packages/pkg_examples/pib_topic_template/modules/topic_template_timed_publisher.py  –  50 Zeilen geprüft
packages/pkg_examples/pib_topic_template/modules/topic_template_triggered_publisher.py  –  45 Zeilen geprüft
packages/pkg_examples/pib_topic_template/package.xml  –  22 Zeilen geprüft
packages/pkg_examples/pib_topic_template/setup.cfg  –  5 Zeilen geprüft
packages/pkg_examples/pib_topic_template/setup.py  –  31 Zeilen geprüft
packages/pkg_gestures/Dockerfile  –  36 Zeilen geprüft
packages/pkg_gestures/README.md  –  14 Zeilen geprüft
packages/pkg_gestures/config/gestures.launch.py  –  30 Zeilen geprüft
packages/pkg_gestures/docker-compose.yaml  –  19 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/CMakeLists.txt  –  16 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/LICENSE  –  203 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/README.md  –  252 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/__init__.py  –  1 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/__init__.py  –  1 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/.gitignore  –  1 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/LICENSE  –  1 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/README.md  –  224 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/pyproject.toml  –  31 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/__init__.py  –  1 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/classes/__init__.py  –  3 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/classes/matrices.py  –  48 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/classes/vectors.py  –  38 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/config/__init__.py  –  3 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/config/gestures.py  –  191 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/config/param.py  –  74 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core/__init__.py  –  4 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core/greet_person.py  –  119 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core/look_at.py  –  77 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core/point_to.py  –  101 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/greet_person.py  –  57 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/logging_utils/__init__.py  –  1 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/logging_utils/core.log  –  3899 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/logging_utils/logger.config  –  75 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/logging_utils/logic.log  –  1 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/logging_utils/pib_control.log  –  1 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/logging_utils/transform.log  –  1 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/look_at.py  –  44 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/point_to.py  –  75 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/utils/__init__.py  –  4 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/utils/logic.py  –  76 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/utils/pib_control.py  –  31 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/src/pib_gestures/utils/transform.py  –  215 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/tests/test_greet_person.py  –  15 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures/tests/test_point_to.py  –  16 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures_client.py  –  155 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/modules/pib_gestures_server.py  –  133 Zeilen geprüft
packages/pkg_gestures/pib_gestures_action/package.xml  –  24 Zeilen geprüft
packages/pkg_interfaces/PKG_IGNORE  –  2 Zeilen geprüft
packages/pkg_interfaces/README.md  –  14 Zeilen geprüft
packages/pkg_interfaces/georg_gesture_msgs/CMakeLists.txt  –  16 Zeilen geprüft
packages/pkg_interfaces/georg_gesture_msgs/action/PibGesturesInterface.action  –  11 Zeilen geprüft
packages/pkg_interfaces/georg_gesture_msgs/package.xml  –  23 Zeilen geprüft
packages/pkg_interfaces/georg_nav_msgs/CMakeLists.txt  –  22 Zeilen geprüft
packages/pkg_interfaces/georg_nav_msgs/action/DriveRoute.action  –  27 Zeilen geprüft
packages/pkg_interfaces/georg_nav_msgs/action/Navigate.action  –  33 Zeilen geprüft
packages/pkg_interfaces/georg_nav_msgs/package.xml  –  23 Zeilen geprüft
packages/pkg_interfaces/georg_task_manager_msgs/CMakeLists.txt  –  22 Zeilen geprüft
packages/pkg_interfaces/georg_task_manager_msgs/msg/MissionStatus.msg  –  14 Zeilen geprüft
packages/pkg_interfaces/georg_task_manager_msgs/package.xml  –  22 Zeilen geprüft
packages/pkg_interfaces/georg_task_manager_msgs/srv/ApprovePlan.srv  –  6 Zeilen geprüft
packages/pkg_interfaces/georg_task_manager_msgs/srv/CancelMission.srv  –  6 Zeilen geprüft
packages/pkg_interfaces/georg_task_manager_msgs/srv/Instruct.srv  –  8 Zeilen geprüft
packages/pkg_interfaces/georg_task_manager_msgs/srv/ListMissions.srv  –  5 Zeilen geprüft
packages/pkg_interfaces/georg_task_manager_msgs/srv/SetMode.srv  –  7 Zeilen geprüft
packages/pkg_interfaces/georg_task_manager_msgs/srv/StartMission.srv  –  7 Zeilen geprüft
packages/pkg_llm/README.md  –  30 Zeilen geprüft
packages/pkg_llm/docker-compose.yaml  –  25 Zeilen geprüft
packages/pkg_navigation/Dockerfile  –  25 Zeilen geprüft
packages/pkg_navigation/README.md  –  186 Zeilen geprüft
packages/pkg_navigation/config/navigation.launch.py  –  58 Zeilen geprüft
packages/pkg_navigation/docker-compose.yaml  –  26 Zeilen geprüft
packages/pkg_navigation/drive_route_server_pkg/drive_route_server/__init__.py  –  1 Zeilen geprüft
packages/pkg_navigation/drive_route_server_pkg/drive_route_server/drive_route_action_server.py  –  557 Zeilen geprüft
packages/pkg_navigation/drive_route_server_pkg/drive_route_server/drive_route_client.py  –  114 Zeilen geprüft
packages/pkg_navigation/drive_route_server_pkg/drive_route_server/mecanum_controller.py  –  126 Zeilen geprüft
packages/pkg_navigation/drive_route_server_pkg/package.xml  –  26 Zeilen geprüft
packages/pkg_navigation/drive_route_server_pkg/resource/drive_route_server  –  1 Zeilen geprüft
packages/pkg_navigation/drive_route_server_pkg/setup.cfg  –  5 Zeilen geprüft
packages/pkg_navigation/drive_route_server_pkg/setup.py  –  29 Zeilen geprüft
packages/pkg_navigation/navigate_server_pkg/navigate_server/__init__.py  –  1 Zeilen geprüft
packages/pkg_navigation/navigate_server_pkg/navigate_server/astar.py  –  214 Zeilen geprüft
packages/pkg_navigation/navigate_server_pkg/navigate_server/grid_rasterizer.py  –  281 Zeilen geprüft
packages/pkg_navigation/navigate_server_pkg/navigate_server/navigate_action_server.py  –  259 Zeilen geprüft
packages/pkg_navigation/navigate_server_pkg/package.xml  –  26 Zeilen geprüft
packages/pkg_navigation/navigate_server_pkg/resource/navigate_server  –  1 Zeilen geprüft
packages/pkg_navigation/navigate_server_pkg/setup.cfg  –  5 Zeilen geprüft
packages/pkg_navigation/navigate_server_pkg/setup.py  –  29 Zeilen geprüft
packages/pkg_object_detection/Datensatz/images/train/20260708_145237.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_145357.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_145736.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_145821.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_150122.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_150405.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_150445.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_150506.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_150607.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_150853.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_151131.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_151213.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_151224.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_151245.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_151304.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_151324.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_151530.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_172723.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_172917.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_173421.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_173547.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_173722.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_173914.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_174702.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_174717.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_174719.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_174725.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_174735.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_174806.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_174844.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_174909.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_174950.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_174953.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_175001.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_175025.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_175100.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_182154.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_182211.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_182435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_182440.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_182507.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_182511.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_182610.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_182859.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_182921.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183159.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183221.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183223.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183251.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183254.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183301.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183325.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183331.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183405.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183420.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183459.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183509.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183534.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183545.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_183550.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_184757.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_184830.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_184922.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_184953.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_184959.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185016.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185045.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185114.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185215.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185235.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185325.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185332.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185339.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185420.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185427.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185446.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185449.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185533.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185538.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185600.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185603.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185606.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185611.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185716.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185719.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185751.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_185803.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_190243.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_190249.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_190256.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_190339.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_190355.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_190504.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_190538.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_190552.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_192915.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193022.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193120.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193206.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193218.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193309.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193314.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193426.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193434.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193518.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193531.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193630.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193659.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193707.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193800.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193814.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193821.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_193931.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_194037.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_194116.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_194151.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_194155.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_194201.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_194301.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_194315.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_194319.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_195825.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_195852.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_195927.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_195941.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200623.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200627.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200632.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200641.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200657.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200659.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200704.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200708.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200715.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200718.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200728.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200733.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200738.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200742.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200815.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200818.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200821.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200848.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200850.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200853.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200857.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200910.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200912.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200914.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200918.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200944.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200946.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200948.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_200955.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201003.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201006.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201009.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201030.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201040.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201043.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201046.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201134.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201136.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201141.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201146.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201152.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201157.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201210.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201216.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201218.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201220.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201228.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201236.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201238.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201240.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201242.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201253.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201302.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201304.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201306.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201309.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201312.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201314.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201318.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201327.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201331.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201336.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201345.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201347.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201405.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201415.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201417.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201420.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201432.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201437.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201440.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201444.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201451.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201454.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201456.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201500.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201502.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201509.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201512.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201514.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201519.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201521.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201525.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201529.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201556.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201559.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201602.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201605.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201618.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201620.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201623.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201628.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201636.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201639.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201641.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201643.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201652.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201655.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201657.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201700.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201705.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201708.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201710.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201717.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201719.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201722.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201725.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201749.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201751.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201754.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201805.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201807.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201812.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201818.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201824.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201828.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201831.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201833.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201841.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_201845.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202002.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202004.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202008.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202013.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202018.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202020.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202025.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202027.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202031.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202036.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202038.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202040.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202046.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202052.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202059.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202101.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202119.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202121.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202129.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202152.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202157.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202201.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202216.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202221.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202229.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202259.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202301.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202303.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202312.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202321.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202324.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202334.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202336.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202341.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202344.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202348.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202356.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202359.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202402.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202409.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202412.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202516.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202518.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202521.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202524.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202529.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202536.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202539.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202541.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202547.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202553.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202555.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202600.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202602.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202605.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202624.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202625.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202627.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202629.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202638.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202639.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202642.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202645.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202651.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202654.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202656.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202659.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202702.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202710.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202713.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202716.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202724.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202742.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202745.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202753.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202756.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202806.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202811.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202817.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202823.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202826.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202831.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202834.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202836.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202840.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202844.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202848.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202850.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202855.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202901.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202916.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202922.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202941.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202943.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202947.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202951.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_202953.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203006.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203012.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203026.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203028.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203032.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203051.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203053.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203057.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203102.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203105.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203110.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203118.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203121.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203125.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203133.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203136.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203143.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203148.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203232.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203234.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203237.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203239.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203255.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203257.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203300.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203302.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203306.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203308.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203311.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203314.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203321(0).jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203321.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203324.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203328.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203338.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203340.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203344.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203359.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203401.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203404.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203409.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203411.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203413.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203414.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203419.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203421.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203422.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203427.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203429.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203431.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203442.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203447.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203451.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203457.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203511.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203513.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203515.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203517.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203529.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203530.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203540.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203542.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203544.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203547.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203603.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203606.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203609.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203612.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203617.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203619.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203622.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203624.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203654.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203701.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203704.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203718.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203721.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203725.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203727.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203729.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203734.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203739.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203743.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203746.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203751.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203756.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203801.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203807.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203810.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203814.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203820.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203822.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260708_203825.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125800.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125804.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125810.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125813.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125817.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125838.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125841.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125848.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125901.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125903.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125909.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125913.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_125934.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130043.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130058.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130106.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130215.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130219.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130233.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130237.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130249.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130255.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130258.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130328.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130331.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130336.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130417.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130422.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130438.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130442.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130501.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130506.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130517.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130530.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130656.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130658.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130709.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130713.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130716.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130719.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130723.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130725.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130728.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130730.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130741.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130745.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130748.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130750.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130753.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130755.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130800.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130826.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130840.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130843.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130857.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130901.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130904.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130907.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130915.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130923.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130928.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130934.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130936.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_130940.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131134.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131136.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131141.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131159.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131201.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131204.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131207.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131209.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131229.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131232.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131234.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131239.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131250.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131256.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131303.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131315.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131317.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131322.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131328.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131437.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131441.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131445.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131509.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131513.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131516.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131535.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131541.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131544.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131549.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131605.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131611.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131636.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131639.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131706.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131712.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131715.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131743.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131756.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131801.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131950.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131953.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_131957.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132002.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132005.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132025.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132044.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132059.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132120.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132124.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132158.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132203.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132207.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132228.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132235.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132303.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132320.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132327.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132338.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132356.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132358.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132441.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132452.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132456.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132507.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132510.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132513.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132517.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132707.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132710.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132715.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132717.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132720.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132747.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132750.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132756.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132758.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132802.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132805.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132807.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132821.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132824.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132827.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132846.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132849.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132903.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132917.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132926.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132941.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132955.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_132959.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133008.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133023.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133051.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133055.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133101.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133110.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133117.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133529.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133534.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133544.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133547.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133701.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133704.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133709.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133726.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133731.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133735.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133815.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133819.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133822.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133840.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133850.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133852.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133902.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133921.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133923.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_133928.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134036.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134038.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134043.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134058.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134101.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134108.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134126.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134129.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134132.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134135.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134154.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134200.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134211.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134213.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134223.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134237.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134249.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134351.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134355.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134401.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134406.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134423.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134426.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134442.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134445.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134457.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134459.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134509.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134512.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134534.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134539.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134552.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134555.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134558.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134610.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134616.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134718.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134721.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134724.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134728.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134740.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134743.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134803.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134806.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134818.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134821.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134833.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134837.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134843.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134846.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134902.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134916.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134930.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134932.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134947.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_134950.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135513.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135515.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135519.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135523.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135535.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135537.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135539.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135547.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135549.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135551.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135606.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135608.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135610.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135625.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135626.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135628.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135700.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135706.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135713.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135716.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135726.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135739.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135741.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135746.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135750.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135810.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135813.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135816.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_135819.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140021.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140023.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140028.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140032.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140050.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140058.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140101.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140104.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140106.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140132.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140137.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140141.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140145.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140236.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140238.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140253.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140301.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140303.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140305.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140309.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140313.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140316.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140319.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140325.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140339.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140342.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260713_140344.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164429.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164431.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164438.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164442.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164459.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164502.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164504.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164506.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164509.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164522.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164524.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164527.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164530.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164534.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164617.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164629.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164632.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164636.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164756.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164759.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164802.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164822.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164952.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164955.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_164958.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165001.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165015.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165017.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165019.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165022.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165043.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165045.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165104.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165106.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165108.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165110.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165145.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165147.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165150.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165206.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165208.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165225.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165228.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165231.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165255.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165257.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165300.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165328.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165331.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165334.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165337.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165350.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165354.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165358.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165411.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165415.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165454.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165457.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165500.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165503.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165508.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165526.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165529.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_165538.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171337.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171352.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171355.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171412.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171418.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171444.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171449.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171454.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171511.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171514.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171517.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171523.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171603.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171608.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171614.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171649.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171653.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171659.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171702.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171724.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171728.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171750.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171753.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_171757.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_172655.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_172713.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_172733.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_172829.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_172841.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_172913.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173022.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173027.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173045.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173118.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173142.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173156.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173212.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173253.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173256.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173301.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173317.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173323.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173344.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173348.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173351.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173404.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173703.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173707.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173711.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173729.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173732.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173735.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173804.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173808.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173826.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173831.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173839.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173855.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173907.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173910.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173944.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173946.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_173950.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174004.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174007.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174017.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174020.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174040.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174044.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174056.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174059.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174121.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174124.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174207.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174213.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174224.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174228.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174248.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174251.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174308.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174326.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174329.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174344.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174356.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174402.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174411.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174736.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174739.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174748.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174808.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174813.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174824.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174851.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174854.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174910.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174921.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174924.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174937.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174940.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174954.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_174959.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175001.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175136.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175138.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175141.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175156.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175158.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175201.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175203.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175212.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175214.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175217.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175250.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175255.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175300.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175324.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175328.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175332.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175339.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175404.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175407.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175411.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175427.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175429.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175433.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175451.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175454.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/train/20260714_175456.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154301.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154303.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154307.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154355.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154358.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154402.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154405.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154408.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154434.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154443.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154446.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154503.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154510.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154513.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_154516.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155019.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155021.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155143.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155146.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155202.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155205.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155214.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155217.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155234.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155238.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155244.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155259.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155302.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155307.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155340.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155513.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155516.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155518.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155523.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155540.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155543.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155603.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155607.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155628.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155633.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155657.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155701.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155744.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155747.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155809.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155837.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155839.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155843.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155854.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155856.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155859.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155903.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155918.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155926.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155929.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155947.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_155950.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160002.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160007.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160103.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160105.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160108.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160110.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160114.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160116.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160118.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160124.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160126.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_160128.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162038.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162040.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162048.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162050.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162054.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162056.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162058.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162103.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162105.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162107.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162111.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162113.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162210.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162219.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162223.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162245.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162248.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162307.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162329.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162332.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162342.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162348.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162413.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162416.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162438.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162715.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162720.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162722.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162745.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162748.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162751.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162809.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162811.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162815.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162838.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162841.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162903.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162906.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_162909.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163026.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163031.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163037.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163040.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163050.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163053.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163118.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163129.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163132.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163148.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163151.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163208.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163210.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163213.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163228.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163230.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163352.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163354.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163357.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163401.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163413.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163415.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163418.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163431.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163436.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163449.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163451.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163453.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163512.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/images/val/20260714_163528.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Datensatz/labels/train/20260708_145237.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_145357.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_145736.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_145821.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_150122.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_150405.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_150445.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_150506.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_150607.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_150853.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_151131.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_151213.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_151224.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_151245.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_151304.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_151324.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_151530.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_172723.txt  –  10 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_172917.txt  –  13 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_173421.txt  –  10 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_173547.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_173722.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_173914.txt  –  10 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_174702.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_174717.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_174719.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_174725.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_174735.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_174806.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_174844.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_174909.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_174950.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_174953.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_175001.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_175025.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_175100.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_182154.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_182211.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_182435.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_182440.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_182507.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_182511.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_182610.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_182859.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_182921.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183159.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183221.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183223.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183251.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183254.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183301.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183325.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183331.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183405.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183420.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183459.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183509.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183534.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183545.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_183550.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_184757.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_184830.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_184922.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_184953.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_184959.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185016.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185045.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185114.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185215.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185235.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185325.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185332.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185339.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185420.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185427.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185446.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185449.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185533.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185538.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185600.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185603.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185606.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185611.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185716.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185719.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185751.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_185803.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_190243.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_190249.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_190256.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_190339.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_190355.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_190504.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_190538.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_190552.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_192915.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193022.txt  –  11 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193120.txt  –  13 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193206.txt  –  13 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193218.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193309.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193314.txt  –  16 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193426.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193434.txt  –  10 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193518.txt  –  16 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193531.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193630.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193659.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193707.txt  –  12 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193800.txt  –  12 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193814.txt  –  17 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193821.txt  –  14 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_193931.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_194037.txt  –  10 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_194116.txt  –  17 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_194151.txt  –  13 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_194155.txt  –  13 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_194201.txt  –  13 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_194301.txt  –  14 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_194315.txt  –  17 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_194319.txt  –  17 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_195825.txt  –  16 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_195852.txt  –  16 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_195927.txt  –  16 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_195941.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200623.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200627.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200632.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200641.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200657.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200659.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200704.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200708.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200715.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200718.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200728.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200733.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200738.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200742.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200815.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200818.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200821.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200848.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200850.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200853.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200857.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200910.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200912.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200914.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200918.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200944.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200946.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200948.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_200955.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201003.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201006.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201009.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201030.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201040.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201043.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201046.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201134.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201136.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201141.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201146.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201152.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201157.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201210.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201216.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201218.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201220.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201228.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201236.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201238.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201240.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201242.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201253.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201302.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201304.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201306.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201309.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201312.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201314.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201318.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201327.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201331.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201336.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201345.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201347.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201405.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201415.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201417.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201420.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201432.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201435.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201437.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201440.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201444.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201451.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201454.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201456.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201500.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201502.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201509.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201512.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201514.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201519.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201521.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201525.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201529.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201556.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201559.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201602.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201605.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201618.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201620.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201623.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201628.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201636.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201639.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201641.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201643.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201652.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201655.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201657.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201700.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201705.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201708.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201710.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201717.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201719.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201722.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201725.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201749.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201751.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201754.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201805.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201807.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201812.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201818.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201824.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201828.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201831.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201833.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201841.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_201845.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202002.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202004.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202008.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202013.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202018.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202020.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202025.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202027.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202031.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202036.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202038.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202040.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202046.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202052.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202059.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202101.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202119.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202121.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202129.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202152.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202157.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202201.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202216.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202221.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202229.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202259.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202301.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202303.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202312.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202321.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202324.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202334.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202336.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202341.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202344.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202348.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202356.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202359.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202402.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202409.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202412.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202516.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202518.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202521.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202524.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202529.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202536.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202539.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202541.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202547.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202553.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202555.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202600.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202602.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202605.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202624.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202625.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202627.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202629.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202638.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202639.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202642.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202645.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202651.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202654.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202656.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202659.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202702.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202710.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202713.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202716.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202724.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202742.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202745.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202753.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202756.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202806.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202811.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202817.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202823.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202826.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202831.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202834.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202836.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202840.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202844.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202848.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202850.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202855.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202901.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202916.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202922.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202941.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202943.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202947.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202951.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_202953.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203006.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203012.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203026.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203028.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203032.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203051.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203053.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203057.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203102.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203105.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203110.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203118.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203121.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203125.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203133.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203136.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203143.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203148.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203232.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203234.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203237.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203239.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203255.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203257.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203300.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203302.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203306.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203308.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203311.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203314.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203321(0).txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203321.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203324.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203328.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203338.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203340.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203344.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203359.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203401.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203404.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203409.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203411.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203413.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203414.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203419.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203421.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203422.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203427.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203429.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203431.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203435.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203442.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203447.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203451.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203457.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203511.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203513.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203515.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203517.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203529.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203530.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203540.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203542.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203544.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203547.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203603.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203606.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203609.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203612.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203617.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203619.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203622.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203624.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203654.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203701.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203704.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203718.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203721.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203725.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203727.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203729.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203734.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203739.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203743.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203746.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203751.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203756.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203801.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203807.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203810.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203814.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203820.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203822.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260708_203825.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125800.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125804.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125810.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125813.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125817.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125838.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125841.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125848.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125901.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125903.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125909.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125913.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_125934.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130043.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130058.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130106.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130215.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130219.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130233.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130237.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130249.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130255.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130258.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130328.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130331.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130336.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130417.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130422.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130438.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130442.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130501.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130506.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130517.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130530.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130656.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130658.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130709.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130713.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130716.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130719.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130723.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130725.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130728.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130730.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130741.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130745.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130748.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130750.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130753.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130755.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130800.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130826.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130840.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130843.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130857.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130901.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130904.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130907.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130915.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130923.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130928.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130934.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130936.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_130940.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131134.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131136.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131141.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131159.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131201.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131204.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131207.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131209.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131229.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131232.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131234.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131239.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131250.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131256.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131303.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131315.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131317.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131322.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131328.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131435.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131437.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131441.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131445.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131509.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131513.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131516.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131535.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131541.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131544.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131549.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131605.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131611.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131636.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131639.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131706.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131712.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131715.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131743.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131756.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131801.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131950.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131953.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_131957.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132002.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132005.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132025.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132044.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132059.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132120.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132124.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132158.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132203.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132207.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132228.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132235.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132303.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132320.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132327.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132338.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132356.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132358.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132435.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132441.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132452.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132456.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132507.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132510.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132513.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132517.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132707.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132710.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132715.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132717.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132720.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132747.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132750.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132756.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132758.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132802.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132805.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132807.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132821.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132824.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132827.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132846.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132849.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132903.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132917.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132926.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132941.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132955.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_132959.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133008.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133023.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133051.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133055.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133101.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133110.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133117.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133529.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133534.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133544.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133547.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133701.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133704.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133709.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133726.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133731.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133735.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133815.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133819.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133822.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133840.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133850.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133852.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133902.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133921.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133923.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_133928.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134036.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134038.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134043.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134058.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134101.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134108.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134126.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134129.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134132.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134135.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134154.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134200.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134211.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134213.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134223.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134237.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134249.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134351.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134355.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134401.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134406.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134423.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134426.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134442.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134445.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134457.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134459.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134509.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134512.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134534.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134539.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134552.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134555.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134558.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134610.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134616.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134718.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134721.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134724.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134728.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134740.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134743.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134803.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134806.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134818.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134821.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134833.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134837.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134843.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134846.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134902.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134916.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134930.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134932.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134947.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_134950.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135513.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135515.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135519.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135523.txt  –  9 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135535.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135537.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135539.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135547.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135549.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135551.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135606.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135608.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135610.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135625.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135626.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135628.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135700.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135706.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135713.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135716.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135726.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135739.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135741.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135746.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135750.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135810.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135813.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135816.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_135819.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140021.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140023.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140028.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140032.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140050.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140058.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140101.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140104.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140106.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140132.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140137.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140141.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140145.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140236.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140238.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140253.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140301.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140303.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140305.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140309.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140313.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140316.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140319.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140325.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140339.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140342.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260713_140344.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164429.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164431.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164435.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164438.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164442.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164459.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164502.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164504.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164506.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164509.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164522.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164524.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164527.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164530.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164534.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164617.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164629.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164632.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164636.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164756.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164759.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164802.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164822.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164952.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164955.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_164958.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165001.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165015.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165017.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165019.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165022.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165043.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165045.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165104.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165106.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165108.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165110.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165145.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165147.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165150.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165206.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165208.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165225.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165228.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165231.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165255.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165257.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165300.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165328.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165331.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165334.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165337.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165350.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165354.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165358.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165411.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165415.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165454.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165457.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165500.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165503.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165508.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165526.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165529.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_165538.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171337.txt  –  10 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171352.txt  –  10 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171355.txt  –  10 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171412.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171418.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171444.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171449.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171454.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171511.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171514.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171517.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171523.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171603.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171608.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171614.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171649.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171653.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171659.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171702.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171724.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171728.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171750.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171753.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_171757.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_172655.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_172713.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_172733.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_172829.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_172841.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_172913.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173022.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173027.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173045.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173118.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173142.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173156.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173212.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173253.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173256.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173301.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173317.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173323.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173344.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173348.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173351.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173404.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173703.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173707.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173711.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173729.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173732.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173735.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173804.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173808.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173826.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173831.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173839.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173855.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173907.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173910.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173944.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173946.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_173950.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174004.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174007.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174017.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174020.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174040.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174044.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174056.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174059.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174121.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174124.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174207.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174213.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174224.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174228.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174248.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174251.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174308.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174326.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174329.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174344.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174356.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174402.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174411.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174736.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174739.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174748.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174808.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174813.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174824.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174851.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174854.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174910.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174921.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174924.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174937.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174940.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174954.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_174959.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175001.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175136.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175138.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175141.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175156.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175158.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175201.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175203.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175212.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175214.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175217.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175250.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175255.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175300.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175324.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175328.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175332.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175339.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175404.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175407.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175411.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175427.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175429.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175433.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175451.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175454.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/20260714_175456.txt  –  7 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/train/classes.txt  –  27 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154301.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154303.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154307.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154355.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154358.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154402.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154405.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154408.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154434.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154443.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154446.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154503.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154510.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154513.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_154516.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155019.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155021.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155143.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155146.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155202.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155205.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155214.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155217.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155234.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155238.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155244.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155259.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155302.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155307.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155340.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155513.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155516.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155518.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155523.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155540.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155543.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155603.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155607.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155628.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155633.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155657.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155701.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155744.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155747.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155809.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155837.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155839.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155843.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155854.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155856.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155859.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155903.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155918.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155926.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155929.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155947.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_155950.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160002.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160007.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160103.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160105.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160108.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160110.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160114.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160116.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160118.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160124.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160126.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_160128.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162038.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162040.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162048.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162050.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162054.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162056.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162058.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162103.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162105.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162107.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162111.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162113.txt  –  2 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162210.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162219.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162223.txt  –  8 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162245.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162248.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162307.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162329.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162332.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162342.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162348.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162413.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162416.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162435.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162438.txt  –  6 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162715.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162720.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162722.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162745.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162748.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162751.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162809.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162811.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162815.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162838.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162841.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162903.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162906.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_162909.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163026.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163031.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163037.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163040.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163050.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163053.txt  –  4 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163118.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163129.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163132.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163148.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163151.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163208.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163210.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163213.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163228.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163230.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163352.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163354.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163357.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163401.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163413.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163415.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163418.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163431.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163436.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163449.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163451.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163453.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163512.txt  –  3 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/20260714_163528.txt  –  5 Zeilen geprüft
packages/pkg_object_detection/Datensatz/labels/val/classes.txt  –  27 Zeilen geprüft
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_145237.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_145357.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_145736.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_145821.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_150122.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_150405.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_150445.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_150506.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_150607.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_150853.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_151131.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_151213.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_151224.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_151245.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_151304.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_151324.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_151530.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_172723.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_172917.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_173421.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_173547.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_173722.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_173914.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_174702.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_174717.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_174719.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_174725.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_174735.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_174806.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_174844.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_174909.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_174950.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_174953.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_175001.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_175025.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_175100.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_182154.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_182211.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_182435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_182440.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_182507.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_182511.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_182610.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_182859.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_182921.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183159.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183221.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183223.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183251.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183254.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183301.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183325.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183331.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183405.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183420.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183459.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183509.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183534.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183545.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_183550.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_184757.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_184830.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_184922.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_184953.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_184959.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185016.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185045.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185114.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185215.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185235.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185325.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185332.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185339.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185420.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185427.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185446.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185449.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185533.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185538.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185600.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185603.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185606.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185611.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185716.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185719.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185751.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_185803.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_190243.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_190249.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_190256.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_190339.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_190355.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_190504.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_190538.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_190552.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_192915.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193022.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193120.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193206.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193218.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193309.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193314.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193426.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193434.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193518.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193531.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193630.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193659.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193707.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193800.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193814.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193821.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_193931.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_194037.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_194116.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_194151.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_194155.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_194201.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_194301.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_194315.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_194319.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_195825.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_195852.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_195927.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_195941.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200623.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200627.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200632.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200641.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200657.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200659.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200704.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200708.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200715.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200718.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200728.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200733.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200738.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200742.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200815.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200818.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200821.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200848.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200850.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200853.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200857.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200910.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200912.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200914.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200918.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200944.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200946.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200948.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_200955.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201003.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201006.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201009.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201030.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201040.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201043.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201046.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201134.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201136.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201141.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201146.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201152.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201157.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201210.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201216.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201218.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201220.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201228.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201236.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201238.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201240.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201242.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201253.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201302.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201304.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201306.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201309.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201312.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201314.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201318.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201327.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201331.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201336.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201345.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201347.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201405.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201415.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201417.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201420.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201432.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201437.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201440.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201444.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201451.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201454.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201456.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201500.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201502.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201509.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201512.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201514.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201519.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201521.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201525.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201529.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201556.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201559.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201602.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201605.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201618.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201620.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201623.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201628.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201636.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201639.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201641.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201643.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201652.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201655.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201657.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201700.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201705.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201708.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201710.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201717.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201719.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201722.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201725.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201749.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201751.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201754.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201805.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201807.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201812.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201818.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201824.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201828.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201831.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201833.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201841.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_201845.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202002.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202004.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202008.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202013.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202018.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202020.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202025.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202027.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202031.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202036.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202038.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202040.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202046.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202052.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202059.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202101.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202119.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202121.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202129.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202152.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202157.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202201.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202216.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202221.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202229.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202259.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202301.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202303.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202312.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202321.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202324.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202334.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202336.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202341.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202344.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202348.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202356.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202359.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202402.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202409.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202412.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202516.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202518.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202521.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202524.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202529.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202536.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202539.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202541.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202547.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202553.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202555.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202600.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202602.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202605.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202624.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202625.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202627.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202629.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202638.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202639.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202642.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202645.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202651.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202654.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202656.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202659.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202702.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202710.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202713.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202716.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202724.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202742.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202745.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202753.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202756.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202806.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202811.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202817.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202823.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202826.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202831.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202834.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202836.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202840.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202844.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202848.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202850.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202855.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202901.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202916.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202922.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202941.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202943.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202947.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202951.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_202953.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203006.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203012.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203026.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203028.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203032.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203051.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203053.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203057.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203102.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203105.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203110.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203118.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203121.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203125.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203133.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203136.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203143.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203148.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203232.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203234.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203237.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203239.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203255.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203257.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203300.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203302.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203306.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203308.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203311.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203314.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203321(0).jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203321.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203324.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203328.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203338.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203340.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203344.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203359.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203401.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203404.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203409.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203411.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203413.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203414.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203419.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203421.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203422.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203427.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203429.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203431.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203442.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203447.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203451.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203457.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203511.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203513.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203515.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203517.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203529.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203530.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203540.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203542.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203544.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203547.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203603.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203606.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203609.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203612.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203617.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203619.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203622.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203624.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203654.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203701.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203704.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203718.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203721.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203725.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203727.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203729.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203734.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203739.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203743.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203746.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203751.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203756.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203801.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203807.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203810.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203814.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203820.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203822.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260708_203825.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125800.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125804.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125810.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125813.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125817.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125838.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125841.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125848.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125901.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125903.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125909.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125913.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_125934.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130043.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130058.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130106.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130215.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130219.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130233.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130237.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130249.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130255.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130258.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130328.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130331.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130336.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130417.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130422.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130438.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130442.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130501.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130506.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130517.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130530.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130656.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130658.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130709.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130713.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130716.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130719.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130723.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130725.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130728.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130730.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130741.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130745.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130748.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130750.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130753.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130755.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130800.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130826.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130840.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130843.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130857.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130901.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130904.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130907.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130915.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130923.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130928.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130934.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130936.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_130940.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131134.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131136.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131141.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131159.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131201.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131204.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131207.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131209.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131229.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131232.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131234.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131239.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131250.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131256.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131303.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131315.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131317.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131322.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131328.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131437.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131441.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131445.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131509.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131513.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131516.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131535.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131541.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131544.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131549.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131605.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131611.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131636.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131639.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131706.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131712.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131715.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131743.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131756.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131801.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131950.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131953.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_131957.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132002.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132005.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132025.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132044.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132059.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132120.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132124.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132158.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132203.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132207.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132228.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132235.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132303.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132320.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132327.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132338.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132356.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132358.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132441.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132452.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132456.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132507.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132510.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132513.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132517.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132707.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132710.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132715.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132717.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132720.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132747.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132750.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132756.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132758.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132802.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132805.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132807.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132821.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132824.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132827.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132846.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132849.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132903.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132917.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132926.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132941.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132955.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_132959.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133008.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133023.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133051.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133055.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133101.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133110.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133117.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133529.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133534.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133544.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133547.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133701.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133704.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133709.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133726.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133731.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133735.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133815.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133819.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133822.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133840.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133850.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133852.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133902.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133921.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133923.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_133928.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134036.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134038.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134043.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134058.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134101.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134108.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134126.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134129.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134132.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134135.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134154.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134200.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134211.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134213.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134223.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134237.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134249.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134351.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134355.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134401.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134406.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134423.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134426.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134442.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134445.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134457.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134459.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134509.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134512.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134534.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134539.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134552.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134555.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134558.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134610.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134616.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134718.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134721.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134724.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134728.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134740.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134743.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134803.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134806.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134818.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134821.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134833.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134837.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134843.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134846.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134902.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134916.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134930.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134932.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134947.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_134950.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135513.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135515.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135519.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135523.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135535.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135537.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135539.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135547.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135549.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135551.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135606.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135608.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135610.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135625.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135626.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135628.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135700.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135706.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135713.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135716.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135726.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135739.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135741.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135746.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135750.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135810.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135813.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135816.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_135819.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140021.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140023.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140028.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140032.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140050.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140058.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140101.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140104.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140106.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140132.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140137.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140141.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140145.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140236.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140238.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140253.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140301.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140303.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140305.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140309.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140313.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140316.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140319.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140325.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140339.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140342.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260713_140344.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164429.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164431.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164435.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164438.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164442.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164459.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164502.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164504.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164506.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164509.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164522.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164524.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164527.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164530.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164534.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164617.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164629.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164632.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164636.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164756.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164759.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164802.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164822.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164952.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Ergebnisse/Datensatz/images/train/20260714_164955.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Modell/Konvertiertes_Model/best.rvc2.tar.xz  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/Modell/best.pt  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/PKG_IGNORE  –  2 Zeilen geprüft
packages/pkg_object_detection/README.md  –  13 Zeilen geprüft
packages/pkg_object_detection/yolov8n_aug_coco_results/BoxF1_curve.png  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/BoxPR_curve.png  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/BoxP_curve.png  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/BoxR_curve.png  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/args.yaml  –  113 Zeilen geprüft
packages/pkg_object_detection/yolov8n_aug_coco_results/best.pt  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/confusion_matrix.png  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/confusion_matrix_normalized.png  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/labels.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/last.pt  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/results.csv  –  71 Zeilen geprüft
packages/pkg_object_detection/yolov8n_aug_coco_results/results.png  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/train_batch0.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/train_batch1.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/train_batch2.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/val_batch0_labels.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/val_batch0_pred.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/val_batch1_labels.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/val_batch1_pred.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/val_batch2_labels.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_object_detection/yolov8n_aug_coco_results/val_batch2_pred.jpg  –  binär (Bild/Modell/Archiv), kein Code
packages/pkg_sim/Dockerfile  –  28 Zeilen geprüft
packages/pkg_sim/README.md  –  47 Zeilen geprüft
packages/pkg_sim/config/sim.launch.py  –  24 Zeilen geprüft
packages/pkg_sim/config/sim_stack.launch.py  –  44 Zeilen geprüft
packages/pkg_sim/docker-compose.yaml  –  25 Zeilen geprüft
packages/pkg_sim/georg_sim/georg_sim/__init__.py  –  2 Zeilen geprüft
packages/pkg_sim/georg_sim/georg_sim/mjcf.py  –  71 Zeilen geprüft
packages/pkg_sim/georg_sim/georg_sim/sim2d_node.py  –  166 Zeilen geprüft
packages/pkg_sim/georg_sim/georg_sim/simmj_node.py  –  89 Zeilen geprüft
packages/pkg_sim/georg_sim/georg_sim/world.py  –  103 Zeilen geprüft
packages/pkg_sim/georg_sim/package.xml  –  23 Zeilen geprüft
packages/pkg_sim/georg_sim/resource/georg_sim  –  1 Zeilen geprüft
packages/pkg_sim/georg_sim/setup.cfg  –  5 Zeilen geprüft
packages/pkg_sim/georg_sim/setup.py  –  27 Zeilen geprüft
packages/pkg_sim/georg_sim/test/test_mjcf.py  –  58 Zeilen geprüft
packages/pkg_sim/georg_sim/test/test_world.py  –  47 Zeilen geprüft
packages/pkg_slam/Dockerfile  –  29 Zeilen geprüft
packages/pkg_slam/README.md  –  68 Zeilen geprüft
packages/pkg_slam/config/lidars.launch.py  –  61 Zeilen geprüft
packages/pkg_slam/config/parameters/rf2o_laser_odometry.yaml  –  18 Zeilen geprüft
packages/pkg_slam/config/parameters/scan_merger.yaml  –  30 Zeilen geprüft
packages/pkg_slam/config/parameters/slam_toolbox.yaml  –  79 Zeilen geprüft
packages/pkg_slam/config/pkg_slam.launch.py  –  38 Zeilen geprüft
packages/pkg_slam/config/slam.launch.py  –  79 Zeilen geprüft
packages/pkg_slam/config/slam_mcap.launch.py  –  32 Zeilen geprüft
packages/pkg_slam/config/slam_sim.launch.py  –  31 Zeilen geprüft
packages/pkg_slam/docker-compose.yaml  –  26 Zeilen geprüft
packages/pkg_slam/georg_slam.rviz  –  320 Zeilen geprüft
packages/pkg_slam/maps/Nav_Test.yaml  –  180 Zeilen geprüft
packages/pkg_slam/maps/README.md  –  101 Zeilen geprüft
packages/pkg_slam/tools/mcap_raw_only.py  –  83 Zeilen geprüft
packages/pkg_speech/PKG_IGNORE  –  1 Zeilen geprüft
packages/pkg_speech/README.md  –  54 Zeilen geprüft
packages/pkg_task_manager/Dockerfile  –  60 Zeilen geprüft
packages/pkg_task_manager/README.md  –  213 Zeilen geprüft
packages/pkg_task_manager/config/task_manager.launch.py  –  54 Zeilen geprüft
packages/pkg_task_manager/docker-compose.yaml  –  113 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/README.md  –  91 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/demo_burr.py  –  66 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/Georg.py  –  105 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/__init__.py  –  1 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/burr_app/__init__.py  –  2 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/burr_app/actions.py  –  248 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/burr_app/builder.py  –  134 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/burr_app/llm_actions.py  –  181 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/burr_app/ros_adapter.py  –  69 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/burr_app/service.py  –  156 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/catalog.py  –  126 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/catalog.yaml  –  120 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/interface.py  –  100 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/main.py  –  146 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mission_selector.py  –  56 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/missions/Comparison.py  –  73 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/missions/ComparisonNav.py  –  51 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/missions/DigitalFestival.py  –  34 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/missions/Mock_Test.py  –  24 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/missions/Sim_Test.py  –  22 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/missions/Test_Mapping.py  –  34 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/missions/__init__.py  –  1 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/__init__.py  –  2 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/mock_packages.py  –  188 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/scenarios/abort.yaml  –  3 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/scenarios/all_ok.yaml  –  6 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/scenarios/mcap.yaml  –  8 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/scenarios/one_fails.yaml  –  3 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/scenarios/retry_then_ok.yaml  –  3 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/scenarios/sim_mocks.yaml  –  8 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/scenarios/slow_drive.yaml  –  3 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/scenarios/timeout.yaml  –  3 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/mocks/scenarios/unreachable.yaml  –  3 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/planner/__init__.py  –  2 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/planner/llm_client.py  –  82 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/planner/planner.py  –  164 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/planner/prompts.py  –  126 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/ros_bridge.py  –  412 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/task_manager.py  –  120 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/Gesture.py  –  50 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/GraspPlanning.py  –  90 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/Listening.py  –  64 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/Navigate.py  –  155 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/NavigateObject.py  –  115 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/NavigateRoom.py  –  100 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/ReturnToIdle.py  –  34 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/__init__.py  –  1 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/base.py  –  21 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/priority.py  –  22 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/timeout_watcher.py  –  76 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/georg_task_manager/validator.py  –  173 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/package.xml  –  31 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/resource/georg_task_manager  –  1 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/setup.cfg  –  5 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/setup.py  –  36 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/conftest.py  –  93 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/ros_helpers.py  –  217 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_burr_app.py  –  292 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_copyright.py  –  26 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_flake8.py  –  26 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_lichtblick_bridge.py  –  202 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_llm_integration.py  –  218 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_llm_real.py  –  80 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_mcap_integration.py  –  184 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_pep257.py  –  24 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_planner.py  –  219 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_ros_integration.py  –  116 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_sim_integration.py  –  174 Zeilen geprüft
packages/pkg_task_manager/georg_task_manager/test/test_validator.py  –  142 Zeilen geprüft
packages/pkg_task_manager/pib-audio/README.md  –  184 Zeilen geprüft
packages/pkg_task_manager/pib-audio/requirements.lock.txt  –  187 Zeilen geprüft
packages/pkg_task_manager/pib-audio/requirements.txt  –  12 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/datatypes/CMakeLists.txt  –  21 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/datatypes/action/Listen.action  –  19 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/datatypes/msg/VoiceEvent.msg  –  4 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/datatypes/msg/VoiceTask.msg  –  4 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/datatypes/package.xml  –  24 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/Dockerfile  –  51 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/boot_scripts/ros_voice_assistant_boot.service  –  15 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/boot_scripts/ros_voice_assistant_boot.sh  –  5 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/launch/demo_doorbell_bag.launch.py  –  46 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/launch/demo_doorbell_wav.launch.py  –  42 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/launch/demo_listen_action_doorbell.launch.py  –  41 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/launch/demo_listen_action_speech.launch.py  –  53 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/package.xml  –  31 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/requirements.txt  –  70 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/resource/voice_assistant  –  1 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/setup.cfg  –  5 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/setup.py  –  40 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/__init__.py  –  22 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/demo_doorbell_detector.py  –  34 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/doorbell_audio_stream_detector.py  –  71 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/doorbell_task_manager_demo.py  –  102 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/doorbell_wav_detector.py  –  93 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/listen_action_server.py  –  678 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/speech_task_manager_demo.py  –  142 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/voice_rule_engine.py  –  42 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/voice_task_dispatcher.py  –  34 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/whisper_speech_transcriber.py  –  41 Zeilen geprüft
packages/pkg_task_manager/pib-audio/src/voice_assistant/voice_assistant/yamnet_doorbell_classifier.py  –  63 Zeilen geprüft
packages/pkg_task_manager/wiki/Create-a-New-Task.md  –  454 Zeilen geprüft
packages/pkg_urdf/Dockerfile  –  25 Zeilen geprüft
packages/pkg_urdf/README.md  –  16 Zeilen geprüft
packages/pkg_urdf/docker-compose.yaml  –  20 Zeilen geprüft
packages/pkg_urdf/view_urdf.rviz  –  156 Zeilen geprüft
packages/pkg_viz/Dockerfile  –  38 Zeilen geprüft
packages/pkg_viz/Dockerfile.bridge  –  12 Zeilen geprüft
packages/pkg_viz/README.md  –  37 Zeilen geprüft
packages/pkg_viz/config/georg.rviz  –  355 Zeilen geprüft
packages/pkg_viz/config/operator.launch.py  –  50 Zeilen geprüft
packages/pkg_viz/config/qt5ct/colors/gruvbox-dark.conf  –  6 Zeilen geprüft
packages/pkg_viz/config/qt5ct/colors/gruvbox-light.conf  –  6 Zeilen geprüft
packages/pkg_viz/config/qt5ct/qt5ct.conf  –  8 Zeilen geprüft
packages/pkg_viz/docker-compose.yaml  –  49 Zeilen geprüft
packages/pkg_viz/georg_slam.rviz  –  320 Zeilen geprüft
packages/pkg_viz/lichtblick_panel/.gitignore  –  3 Zeilen geprüft
packages/pkg_viz/lichtblick_panel/README.md  –  47 Zeilen geprüft
packages/pkg_viz/lichtblick_panel/build.py  –  54 Zeilen geprüft
packages/pkg_viz/lichtblick_panel/package.json  –  18 Zeilen geprüft
packages/pkg_viz/lichtblick_panel/src/extension.js  –  213 Zeilen geprüft
packages/pkg_viz/lichtblick_panel/src/model.js  –  146 Zeilen geprüft
packages/pkg_viz/lichtblick_panel/test/model.test.js  –  78 Zeilen geprüft
packages/pkg_viz/lichtblick_panel/test/panel.test.js  –  149 Zeilen geprüft
projectctl.bash  –  256 Zeilen geprüft
system-files/README.md  –  34 Zeilen geprüft
system-files/etc/udev/rules.d/51-autonohm-joystick.rules  –  7 Zeilen geprüft
system-files/etc/udev/rules.d/99-pib-motors.rules  –  12 Zeilen geprüft
system-files/projectctl-completion.bash  –  50 Zeilen geprüft
system-files/setup-PC.sh  –  65 Zeilen geprüft
system-files/setup-robot.sh  –  96 Zeilen geprüft
```

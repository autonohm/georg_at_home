# pkg_pib_bridge

Bridge between Georg's stack and [pib-backend](https://github.com/pib-rocks/pib-backend) for
speech, with a fixed allowlist. Optional: `GEORG_WITH_PIB_BACKEND=1 ./projectctl.bash up sim|real`
(needs pib-backend's Docker network `pib-network`).

One process in two ROS domains: the stack (`ROS_DOMAIN_ID`, 30 in sim, 0 on the robot) and
pib-backend (`PIB_BACKEND_DOMAIN_ID`, 0). This container is the only one in both Docker networks.
Nothing else crosses – in particular no drive or motor commands.

| Stack side | pib-backend |
| --- | --- |
| action `speech/say` (`georg_speech_msgs/Say`) | service `/play_audio_from_speech`, voice `M1`/`de` |
| action `audio/listen` (`georg_speech_msgs/Listen`), SPEECH | action `/record_audio` (speech-to-text) → `transcript` |
| action `audio/listen`, DOORBELL | `PIB_DOORBELL_TOPIC` (`std_msgs/Bool`), none by default → not detected |

**No sensor data** (camera, detections, joint states) crosses: in `sim` the robot sees only the
simulation, like it can only move simulated motors. On the robot the stack and pib-backend share
domain 0; in `mcap` the image comes from the recording.

`PIB_SAY_JOIN=false`: do not wait until spoken – only for machines without a loudspeaker
(otherwise pib-backend's `audio_player` blocks). Keep `true` on the robot, or `greeting` hears
Georg's own voice.

Test: `tests/stack/bridge_check.py` (speak and listen as seen from the stack).

Open: on the robot pib-backend runs on the Pi in the LAN, not in this machine's Docker network
(docs/OPEN_ISSUES.md S4); next: pib poses to `/apply_joint_trajectory` (G1).

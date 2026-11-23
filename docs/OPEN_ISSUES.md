# Open issues

What is still open, who owns it, what was decided. IDs: **N** navigation, **L** SLAM/lidar,
**G** gestures/pib, **S** stack, **T** task manager, **V** voice, **H** housekeeping.
Old numbers (Q…) from the former `OPEN_QUESTIONS.md` in brackets.

## Questions for review

| # | Question | Proposal |
| --- | --- | --- |
| R2 | Remove the RViz container (`pkg_viz` profile `viz`), `pkg_examples`, `pkg_object_detection` (528 MB)? | ask Sam / object detection team first (H1–H3) |
| R4 | Doorbell, microphone, speech in sim | decided: own topic later, worked through in one go (V1, V2) |
| R5 | Default world | decided: `Nav_Test.yaml` default, Arena for demos; switch the world from Lichtblick (S9) |

## Navigation (Nav2 in `pkg_nav2`; `pkg_navigation` removed, still on `main`)

| ID | Issue | Status |
| --- | --- | --- |
| N1 (Q36) | No localisation in the map: pose = `odom` + fixed offset from the map YAML; SLAM pose unused | Nav2: solved (drives in the SLAM `map` frame); on the robot places need a saved SLAM map (N8) |
| N2 (Q31) | Drive server read `odom`; on the robot only `odom/lidar` and `odom/wheel` exist | Nav2 uses TF `odom -> base_footprint`; the task manager's position (`robot.py`, topic `odom`) still needs a source on the robot (N8) |
| N3 (Q33) | Gets stuck at door corners / in narrow passages (cuts corners between waypoints, no stuck detection, no re-plan from an inflated cell); seen in `Arena` (`arena_tour` 5/7) | Nav2: solved in sim – Arena tour 7/7, Wohnung 5/5 goals (2026-11-23) |
| N4 (Q25) | 0.55 m gaps in `Nav_Test.yaml` | open (map of the navigation team) |
| N5 | Planner inflation 0.25 m < half diagonal of the base (0.32 m) | Nav2: footprint 0.50 × 0.42 m, inflation 0.45 m |
| N6 | `FACE_TRAVEL_DIRECTION` off: the robot keeps its heading and drives sideways | Nav2: MPPI Omni without preferred direction; at the goal pib faces the object (`tasks/nav2_go.py`) |
| N7 | Switch to Nav2 (R1) | done: `pkg_navigation` removed from this branch, `NavigateObject` and `NavigateRoom` drive with Nav2 |
| N8 | Real robot: the SLAM map starts where Georg is switched on, so map-YAML places are not SLAM poses. Needs a saved SLAM map (slam_toolbox localization mode) with the places in its frame | open – before `real` with Nav2 (S10) |
| N9 | Goal response of an action can get lost (DDS: "Failed to send goal response"); `wait_for_action_result` then waits forever. `nav2_go` resends after 10 s; the other tasks do not | open – task manager |

## SLAM / lidar (Sam)

| ID | Issue | Status |
| --- | --- | --- |
| L1 (Q35) | `slam.launch.py` publishes `map → odom` twice (static + slam_toolbox) | open, reported |
| L2 (Q30) | In sim, SLAM uses `slam_sim.launch.py` (simulator publishes odom tf) instead of `sim_mode` | open – after Nav2 (simulator → wheel odom only) |
| L3 | `privileged` + `/dev` in `pkg_slam`, `pkg_viz`, `pkg_urdf`, `pkg_examples` (hardware scan) | open, reported |
| L4 | RViz configs still use `/georg/...` topics | open (only matters if RViz stays, R2) |

## Gestures / pib (gesture team, stack)

| ID | Issue | Status |
| --- | --- | --- |
| G1 | `pib_pose` on the robot: `pib_bridge` → pib-backend `/apply_joint_trajectory`, limits (`pkg_pib_model/config/pib_limits.yaml`, pose rejected if outside), dry run unless `PIB_POSE_ENABLE=1` | implemented, untested on the robot (G4) |
| G2 (Q34) | Gesture server reports success but sends no joint command (pib-sdk calls commented out) | open – gesture team; proposal: send `/apply_joint_trajectory` (works in sim via fake motors) |
| G3 (Q14, Q24) | Gesture result `int8 success` instead of `bool success, error_code, message` | open – gesture team |
| G4 | Named poses (`pib_poses.yaml`) computed from the model, not checked on the real pib | open – check at the robot before G1 is enabled |

## Stack

| ID | Issue | Status |
| --- | --- | --- |
| S1 | Healthchecks assume no namespace; `EDU_ROBOT_NAMESPACE` is not passed into containers | open (later) |
| S2 | Tests on two paths: Mac pixi (`dev/macos`) and containers/stack; pixi stack still uses `slam_sim` and no drive chain | open – keep pixi for unit tests only |
| S3 | ~50 MB of meshes on first Lichtblick connection | open – decimate pib meshes |
| S4 | One shared network `pib-network`, domains separate (done). Target: pib-backend on the Jetson. If it stays on the Pi: containers need the LAN (`network_mode: host` or macvlan) – OPERATIONS "Network on the robot" | open – decide before `real` |
| S5 | Simulated camera has no detections (real ones come from the OAK chip) | open – detections from known positions in sim |
| S6 | MuJoCo base is a cylinder, not Georg's mesh | open (low) |
| S8 | `drive` container runs `privileged` with `/dev` also in sim (Sam's compose) | info |
| S9 | Switch the simulation world from Lichtblick: panel row "Load world" publishes `/sim/set_world`; simulator, camera and task manager follow | done |
| S10 | Semantic map: name places automatically from camera detections (YOLO on the OAK, depth) or a VLM (Qwen-VL) | future |

## Task manager

| ID | Issue | Status |
| --- | --- | --- |
| T1 (Q21) | Mission ends `SUCCEEDED` although LOW tasks failed | done: discarded tasks are labelled `(SKIPPED)` in the steps and the final message; a mission where no task succeeded (`ReturnToIdle` does not count) ends `FAILED` |
| T2 (Q19) | flake8 of the old task manager code still red | open (low) |
| T3 (Q4b) | `navigate_server` built into the task manager image (map lookup) | done: own lookup `tasks/base.py load_place` |
| T4 (Q27) | LLM model for the Jetson (1.5B plans weakly) | open – step "LLM" |
| T5 (Q28) | Events (doorbell, speech) do not trigger LLM runs yet | open |

## Voice (pib-backend)

| ID | Issue | Status |
| --- | --- | --- |
| V1 (Q37) | On the Jetson: `audio_player` hung (no loudspeaker), `/record_audio` hangs (no ReSpeaker mic) | test with loudspeaker + mic (low priority) |
| V2 (Q1) | No doorbell source | open – R4 |

## Housekeeping

| ID | Item | Status |
| --- | --- | --- |
| H1 | RViz container in `pkg_viz` | R2 |
| H2 | `pkg_examples` | R2 |
| H3 | `pkg_object_detection` (528 MB dataset in git) | R2 |
| H4 | Old Docker images `*:pre-jetson-20261121` (~20 GB) | user: `docker rmi …` |
| H5 | `.claude/worktrees/` (files owned by root) | user: `sudo rm -rf .claude/worktrees && git worktree prune` |
| H6 | `BlenderScene/` in the repo root (untracked) | user: move/remove |
| H7 | `docs/aufgaben/CODEX_ARENA.md` | remove when the Codex arena work is merged |

## Done (for reference)

Q2/Q3/Q16/Q23 old task manager variants removed · Q4/Q5 interfaces in `pkg_interfaces` · Q7/Q32
command gate replaced by domains · Q8 pib-sdk gitlink · Q10 maps in `pkg_slam/maps` · Q11/Q20 built
and tested in containers on the Jetson (arm64) · Q12 action names · Q13 navigation through
`twist_mux`/`twist_limiter` · Q15 small fixes · Q17/Q18/Q22 structure, Burr runs, style · Q26 robot
model in Lichtblick (Georg + movable pib) · Q29 folder rule (except `georg_sim`) · `pkg_speech`
removed (obsolete) · namespace removed · pib-backend speech bridge · simulated camera · worlds.

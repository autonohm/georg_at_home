# Open issues

What is still open, who owns it, what was decided. IDs: **N** navigation, **L** SLAM/lidar,
**G** gestures/pib, **S** stack, **T** task manager, **V** voice, **H** housekeeping.
Old numbers (Q…) from the former `OPEN_QUESTIONS.md` in brackets.

## Questions for review

| # | Question | Proposal |
| --- | --- | --- |
| R1 | Switch navigation to Nav2 now (start from Sam's branch `pkg_nav2`)? | yes – solves N1–N5; keep `nav/navigate_object_x` as the task manager's interface via an adapter |
| R2 | Remove the RViz container (`pkg_viz` profile `viz`), `pkg_examples`, `pkg_object_detection` (528 MB)? | ask Sam / object detection team first (H1–H3) |
| R3 | Should a mission with a failed LOW task still end `SUCCEEDED`? | add an outcome "partial" or make key tasks CRITICAL (T1) |
| R4 | Doorbell for `Listening(DOORBELL)`: Home Assistant (runs in pib-backend) or a button? | Home Assistant event → `PIB_DOORBELL_TOPIC` (V2) |
| R5 | Default world for `up sim`: keep `Nav_Test.yaml` (tests) or switch to `Arena.yaml`? | keep `Nav_Test` as default, Arena for demos |

## Navigation (navigation team; Nav2 planned)

| ID | Issue | Status |
| --- | --- | --- |
| N1 (Q36) | No localisation in the map: pose = `odom` + fixed offset from the map YAML; SLAM pose unused | open – Nav2 (AMCL / slam_toolbox localisation) |
| N2 (Q31) | Drive server reads `odom`; on the robot only `odom/lidar` and `odom/wheel` exist | open – Nav2 |
| N3 (Q33) | Gets stuck at door corners / in narrow passages (cuts corners between waypoints, no stuck detection, no re-plan from an inflated cell); seen in `Arena` (`arena_tour` 5/7) | open – Nav2 |
| N4 (Q25) | 0.55 m gaps in `Nav_Test.yaml` | open (map of the navigation team) |
| N5 | Planner inflation 0.25 m < half diagonal of the base (0.32 m) | open – Nav2 footprint |
| N6 | `FACE_TRAVEL_DIRECTION` off: the robot keeps its heading and drives sideways | info – decide with Nav2 |

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
| G1 | `pib_pose` on the robot: `pib_bridge` → pib-backend `/apply_joint_trajectory` with joint limits and dry run | **next (stack)** |
| G2 (Q34) | Gesture server reports success but sends no joint command (pib-sdk calls commented out) | open – gesture team; proposal: send `/apply_joint_trajectory` (works in sim via fake motors) |
| G3 (Q14, Q24) | Gesture result `int8 success` instead of `bool success, error_code, message` | open – gesture team |
| G4 | Named poses (`pib_poses.yaml`) computed from the model, not checked on the real pib | open – check at the robot before G1 is enabled |

## Stack

| ID | Issue | Status |
| --- | --- | --- |
| S1 | Healthchecks assume no namespace; `EDU_ROBOT_NAMESPACE` is not passed into containers | open (later) |
| S2 | Tests on two paths: Mac pixi (`dev/macos`) and containers/stack; pixi stack still uses `slam_sim` and no drive chain | open – keep pixi for unit tests only |
| S3 | ~50 MB of meshes on first Lichtblick connection | open – decimate pib meshes |
| S4 | On the robot pib-backend runs on the Pi (LAN): `pib_bridge`/`pib_model` need the robot network (host network or macvlan) | open – before `real` |
| S5 | Simulated camera has no detections (real ones come from the OAK chip) | open – detections from known positions in sim |
| S6 | MuJoCo base is a cylinder, not Georg's mesh | open (low) |
| S7 | `projectctl.bash build` exits 0 even when a build fails | open (small) |
| S8 | `drive` container runs `privileged` with `/dev` also in sim (Sam's compose) | info |

## Task manager

| ID | Issue | Status |
| --- | --- | --- |
| T1 (Q21) | Mission ends `SUCCEEDED` although LOW tasks failed | open – R3 |
| T2 (Q19) | flake8 of the old task manager code still red | open (low) |
| T3 (Q4b) | `navigate_server` built into the task manager image (map lookup) | open – goes away with Nav2 adapter |
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

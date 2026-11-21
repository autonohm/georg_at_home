# pkg_pib_model

The movable pib on Georg: visible in Lichtblick, driven by pib-backend on the robot and by fake
motors in the simulation.

```
pib-backend /joint_states (motor names, centidegrees)   sim: fake_pib_motors (same interface)
        │
        ▼
pib_model_node ── pib/joint_states (URDF joints, rad) ──► robot_state_publisher (ns pib) ──► /tf
        │  static tf pib_waist_link → root (mount on Georg), a81_motor_shaft → oak_rgb_camera_optical_frame
        └─ /robot_description (Georg, pkg_urdf) → /georg_full/robot_description
           (Georg without the rigid pib_4S.stl + movable pib) → Lichtblick
```

## Model

The web model of [pib-3d](https://github.com/pib-rocks/pib-3d) (what Cerebra shows), release
`v0.11.6` with SHA-256 – the same pin as `pib-backend/robot_model_version.txt`. It is downloaded at
image build, not kept in git; a new version only needs `PIB_MODEL_VERSION`/`PIB_MODEL_SHA256` in
`Dockerfile` and `pkg_viz/Dockerfile.bridge`.

`model.json` is already a URDF in JSON (47 links with one GLB each, 48 joints);
`pib_model/convert.py` converts it. GLB meshes get a visual origin of −90° about x because
Lichtblick turns every GLB by +90° (its *Mesh up axis* setting only applies to STL/OBJ).

## Joint angles

As in Cerebra (`@pib/robot-view`): URDF angle [°] = motor angle [centideg/100] · `gearRatio` ·
`direction` − `zeroOffsetDeg`; coupled joints (fingers) follow their leading joint · `factor`;
passive joints stay 0. Source: `mapping.json` of the release.

## Mount and head camera

Parameters of `pib_model_node`: `mount_xyz`/`mount_rpy` (pib on `pib_waist_link`, +90° about z,
estimated from the rigid pib mesh), `camera_xyz`/`camera_rpy` (OAK camera on the head link, frame
`oak_rgb_camera_optical_frame` – the frame id of pib-backend's camera images).

## Simulation: fake motors and poses

`fake_pib_motors` (profile `sim` only) behaves like `motor_control` of pib-backend:
`/joint_states` (centidegrees, 10 Hz), `/joint_trajectory` (feedback), service
`/apply_joint_trajectory`, topic `fake_motors/command`. Action `pib/pose`
(`georg_gesture_msgs/PibPose`) drives named poses and sequences from `config/pib_poses.yaml`
(`ruhe`, `winken`, `zeigen`, `begruessen`, …; computed from the model, not yet checked on the
real pib).

## Tests

`cd pib_model_pkg && python3 -m pytest test` (no ROS needed); with
`PIB_MODEL_DIR=<converted model>` also against the real `mapping.json`. In the stack:
`python3 tests/stack/mesh_check.py`.

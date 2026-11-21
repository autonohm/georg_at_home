# Simulation assets

Large source files of the simulation world. They are **not in plain git** (`.gitignore`);
put them here by hand, or move them to Git LFS (not needed now: the simulation worlds are generated, see docs/OPERATIONS.md).

## arena/ – RoboCup@Home competition arena

| File | Size | SHA-256 | What it is |
| --- | --- | --- | --- |
| `Competition_Arena_AtHome.usdc` | 77 MB | `0c176b1afe53ebed8e63fd19c6aed3dc28885cbbe735d9eacca64cd4c1796b91` | USD scene for Isaac Sim; source for the MuJoCo world and the navigation map |
| `Competition_Arena_AtHome.blend` | 215 MB | `32df1b6d3fb10f5d04102d6dccfcf5812a390599471fc4880e626468598f9e90` | Blender scene the USD was made from (edit here) |
| `arena_360_20260929.jpg` | 12 MB | `f71315ca250772e92d784e83cb2135dba8874b111c710e3e9d4681e321ff994b` | 360° photo of the real arena (8000 × 4000, 2026-09-29), environment light / camera background |

USD scene (checked 2026-11-21): metres, Z up. Arena floor 9 × 9 m
(x −3.22…5.78, y −9.04…−0.04), walls 1.25 m high, three doors, about 40 pieces of
furniture (kitchen, bedroom, living room, office), 1.9 million triangles in total.
The robot in the scene is NVIDIA's "Kaya" with a SICK TIM781 lidar as a stand-in; both are
loaded from the NVIDIA cloud and are not part of the file. A model of Georg is not included.

The Isaac Sim ROS graphs in the scene publish `/scan` (frame `sensor`), odometry, and
subscribe to a Twist command, i.e. the same interface as `georg_sim`.

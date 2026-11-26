# pkg_nav2

[Nav2](https://docs.nav2.org/) (ROS 2 Jazzy) für Georg: fährt zu einer Pose auf der live
SLAM-Karte. Kein `map_server`, kein AMCL: slam_toolbox kartiert und lokalisiert gleichzeitig.

> [!IMPORTANT]
> Auf dem Roboter noch nicht getestet. Vor dem ersten Fahren [ROBOT_TEST.md](ROBOT_TEST.md)
> durchgehen.

## Wie es zusammenhängt

| Braucht | Von |
|---------|-----|
| `/map`, TF `map -> odom` | slam_toolbox (`pkg_slam`) |
| `/odom/wheel`, TF `odom -> base_footprint` | Radodometrie (`pkg_drive`, edu_robot) |
| TF `base_footprint -> base_link -> Lidars` | robot_state_publisher (`pkg_urdf`) |
| `/merged_scan` | laser_scan_merger (`pkg_slam`) |

Ausgang: `cmd_vel/nav` → twist_mux → twist_limiter (`pkg_drive`) → Motoren.
Der Joystick (`cmd_vel/teleop`) hat in twist_mux die höhere Priorität und übersteuert Nav2.

```
controller/behaviors -> cmd_vel_nav -> velocity_smoother -> cmd_vel_smoothed
    -> collision_monitor -> cmd_vel/nav
```

## Dateien

- `config/nav2.launch.py` – nur die Nav2-Knoten, die Georg braucht (controller, planner,
  smoother, behaviors, velocity smoother, collision monitor, BT navigator) plus
  lifecycle manager.
- `config/nav2_params.yaml` – aus den nav2_bringup-Defaults erzeugt, der Kopf listet jede
  Änderung (Mecanum/MPPI Omni, Footprint 0,50 × 0,42 m, Geschwindigkeiten unter dem
  twist_limiter, Frames, Odometrie-Topic `odom/wheel`).
- `config/navigation.launch.py`, `config/parameters/`, `georg_slam.rviz` – Sams erster
  Versuch mit nav2_bringup (mit AMCL/map_server); wird nicht mehr gestartet, bleibt als
  Referenz.

Geplant: Sensorfusion aus Laser, Rädern und IMU ([ROBOT_TEST.md](ROBOT_TEST.md), Abschnitt 8).

## Ausprobieren

```bash
./projectctl.bash build
./projectctl.bash up
# Ziel im map-Frame (map = Startpunkt der SLAM-Karte, also wo Georg eingeschaltet wurde)
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 1.0, y: 0.0}, orientation: {w: 1.0}}}}"
```

In RViz/Foxglove: Costmaps `/global_costmap/costmap`, `/local_costmap/costmap`, Pfad `/plan`.

## Herkunft

Begonnen auf Sams Branch `pkg_nav2`, ausgearbeitet und in der Simulation getestet auf
`pkg_task_manager_burr` (Arena 7/7, Wohnung 5/5 Ziele), für `main` und den Roboter angepasst.

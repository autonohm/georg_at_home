# Nav2 am Roboter testen

Anleitung für den ersten Test von `pkg_nav2` auf Georg. Ziel: Branch `pkg_nav2` holen, bauen,
Schritt für Schritt prüfen, danach Merge nach `main`.

**Stand:** In der Simulation fährt dieses Nav2-Setup zuverlässig (Branch
`pkg_task_manager_burr`). Auf dem Roboter ist es **noch nie gelaufen**. Die Änderungen unten
beheben die Fehler aus Sams letztem Versuch am Roboter, sind aber nur am Code und an den Logs
hergeleitet, nicht getestet.

## 1. Was beim letzten Versuch schiefging

Log vom Roboter (Sams Branch, Start über `nav2_bringup`):

```
[collision_monitor]: Robot to stop due to invalid source ...
[getTransform]: Failed to get "base_link"->"base_footprint" frame transform: Lookup would
  require extrapolation into the future. Requested time ...153.5198 but the latest data is at
  time ...153.5080, when looking up transform from frame [odom] to frame [base_footprint]
[global_costmap]: Message Filter dropping message: frame 'base_link' ... for reason 'the
  timestamp on the message is earlier than all the data in the transform cache'
```

Deutung:

- Die Kollisionsüberwachung braucht `odom -> base_footprint` zum aktuellen Zeitpunkt und
  wartet dafür bis zu `transform_tolerance` (damals 0,2 s). In dieser Zeit kam **keine** neue
  Odometrie-TF an. Der Roboter wird daher immer wieder gestoppt.
- Die globale Costmap verwirft Scans, weil der TF-Speicher widersprüchlich ist.

Ursachen im Code auf `main`:

1. **`odom -> base_footprint` hatte zwei Quellen:** rf2o (Laser-Odometrie, `pkg_slam`,
   `publish_tf: true`) und der Radantrieb edu_robot (`pkg_drive`,
   `odometry.publishing_tf: true`). Zwei Quellen für dieselbe TF überschreiben sich
   gegenseitig.
2. **`map -> odom` hatte zwei Quellen:** eine statische Null-TF in
   `pkg_slam/config/slam.launch.py` und slam_toolbox selbst (`transform_publish_period 0.02`).
3. `nav2_bringup` startet zusätzlich Lokalisierung (AMCL, map_server), die ebenfalls
   `map -> odom` veröffentlichen kann und auf Georg nicht gebraucht wird.

## 2. Was auf diesem Branch geändert ist

| Datei | Änderung |
|-------|----------|
| `pkg_nav2/config/nav2.launch.py` | Eigener Launch statt `nav2_bringup`: nur die nötigen Knoten, kein AMCL/map_server |
| `pkg_nav2/config/nav2_params.yaml` | Parameter für Georg (Kopf der Datei listet alles). Odometrie-Topic `odom/wheel`. Kollisionsüberwachung `transform_tolerance` 0,5 s |
| `pkg_nav2/docker-compose.yaml`, `Dockerfile` | Startet den eigenen Launch. Ohne Compose-Profile, die `main` nicht kennt |
| `pkg_slam/config/slam.launch.py` | Statische `map -> odom` entfernt. rf2o veröffentlicht seine TF nur noch im Sim-Modus (Topic `odom/lidar` bleibt) |

Danach gilt auf dem Roboter:

```
map --(slam_toolbox)--> odom --(edu_robot, Räder)--> base_footprint --(urdf)--> base_link
```

## 3. Annahmen, die der Test bestätigen muss

- **A1 (größtes Risiko):** edu_robot veröffentlicht die TF `odom -> base_footprint` (laut
  `edu_robot.yaml`: `odometry.publishing_tf: true`, `footprint_frame: base_footprint`).
  **Achtung:** In Sams Aufnahme `odomtest` meldet `/georg/odom/wheels` als Kind-Frame
  `georg/base_link`, nicht `base_footprint`. Veröffentlicht edu_robot die TF ebenso nach
  `base_link`, hat `base_link` zwei Eltern (Odometrie und URDF) und der TF-Baum ist kaputt.
  Das ist der erste Punkt in Schritt 2.
- **A2:** Die Radodometrie ist für SLAM gut genug. Bei Mecanum rutschen die Räder. slam_toolbox
  korrigiert über den Scan, das ist aber die Stelle mit dem größten Risiko. Alternative siehe 6.
- **A3:** Alle Topics ohne Namespace (`/merged_scan`, `/odom/wheel`, `/cmd_vel/nav`), so wie
  `main` aktuell startet. Sams alte Aufnahme nutzte noch `/georg/...`.
- **A4:** Die Odometrie-TF kommt mit 10 Hz (`publishing_interval_ms: 100`), in der Aufnahme
  mit Lücken bis 0,2 s. Das passt genau zum alten Fehlerbild (Toleranz 0,2 s). Deshalb jetzt
  0,5 s in der Kollisionsüberwachung.

## 4. Vorbereitung

```bash
git fetch && git switch pkg_nav2 && git pull
./projectctl.bash build        # nav2-Image ist neu, dauert beim ersten Mal
./projectctl.bash up
./projectctl.bash logs nav2    # in einem eigenen Terminal offen lassen
```

ROS-Befehle unten im nav2-Container ausführen:

```bash
docker ps --format '{{.Names}}' | grep nav2          # Name, z. B. georg-nav2-1
docker exec -it georg-nav2-1 bash
source /opt/ros/jazzy/setup.bash
```

**Sicherheit:** Beim ersten Fahren Joystick in der Hand. Teleop hat in twist_mux die höhere
Priorität und übersteuert Nav2 sofort. Am besten zuerst aufgebockt (Räder frei).

## 5. Testschritte

Jeden Schritt erst abhaken, dann zum nächsten. Bei Abweichung: Abschnitt 6.

### Schritt 1 – Sensoren und Odometrie laufen

```bash
ros2 topic hz /merged_scan     # erwartet: ~10–15 Hz
ros2 topic hz /odom/wheel      # erwartet: ~10 Hz
ros2 topic hz /odom/lidar      # erwartet: ~14 Hz
ros2 topic hz /map             # erwartet: alle paar Sekunden eine Nachricht
```

### Schritt 2 – Jede TF hat genau eine Quelle (wichtigster Schritt)

```bash
ros2 run tf2_ros tf2_monitor odom base_footprint
ros2 run tf2_ros tf2_monitor map odom
ros2 run tf2_ros tf2_monitor base_footprint base_link
ros2 topic echo /odom/wheel --once | grep frame_id   # erwartet: odom / base_footprint
```

Erwartet: `odom -> base_footprint` nur von edu_robot (`thn_georg_bot`), `map -> odom` nur von
`slam_toolbox`, `base_footprint -> base_link` nur vom `robot_state_publisher`. Kein
`static_transform_publisher` für `map -> odom`. Keine Verzögerung über
~0,2 s. Gesamtbaum zum Ansehen:

```bash
ros2 run tf2_tools view_frames   # erzeugt frames_*.pdf
```

### Schritt 3 – SLAM-Karte ohne Nav2 plausibel

Mit dem Joystick langsam durch den Raum fahren und die Karte in RViz/Foxglove beobachten.
Erwartet: Wände bleiben scharf, die Karte verdreht oder verdoppelt sich nicht. Wenn die Karte
beim Drehen verschmiert: Annahme A2 verletzt, siehe 6.

### Schritt 4 – Nav2 ist hochgefahren

```bash
ros2 lifecycle get /bt_navigator        # erwartet: active [3]
ros2 lifecycle get /controller_server   # erwartet: active [3]
ros2 lifecycle get /collision_monitor   # erwartet: active [3]
```

Im Log von nav2 darf nach dem Start **kein** `extrapolation into the future` und kein
`Robot to stop due to invalid source` mehr dauerhaft auftauchen. Einzelne Meldungen direkt
nach dem Start sind normal.

Costmaps ansehen: `/local_costmap/costmap` und `/global_costmap/costmap`. Hindernisse aus dem
Scan müssen an der richtigen Stelle um den Roboter liegen.

### Schritt 5 – Kurzes Ziel geradeaus

Ziel 1 m vor dem Startpunkt der Karte (map = wo Georg eingeschaltet wurde, x nach vorne):

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 1.0, y: 0.0}, orientation: {w: 1.0}}}}"
```

Erwartet: Pfad auf `/plan`, Roboter fährt langsam hin und meldet `SUCCEEDED`.
Zusätzlich prüfen:

```bash
ros2 topic echo /cmd_vel/nav    # Befehle von Nav2 kommen an
```

### Schritt 6 – Seitlich und Drehung

Ziel `y: 1.0` (links) und ein Ziel mit Drehung (`orientation: {z: 0.707, w: 0.707}` = 90°).
Erwartet: Georg fährt seitlich (Mecanum) und dreht am Ziel.

### Schritt 7 – Hindernis

Während einer Fahrt eine Person/Kiste in den Weg stellen. Erwartet: Georg bremst ab
(Kollisionsüberwachung, `/collision_monitor_state`) und plant um oder wartet.

### Schritt 8 – Längere Strecke

Ziel in einem anderen Raum / durch eine Tür. Erwartet: kein Hängenbleiben an Türkanten.

## 6. Fehlerbilder und was dann hilft

| Beobachtung | Wahrscheinliche Ursache | Was tun |
|-------------|------------------------|---------|
| Schritt 2: edu_robot veröffentlicht `odom -> base_link` statt `odom -> base_footprint` | A1 falsch | Footprint-Frame von edu_robot prüfen (`tf.footprint_frame` in `edu_robot.yaml`). Geht es nicht schnell: Laser-Odometrie als Quelle (Zeile „Karte verschmiert“) |
| Schritt 2: `odom -> base_footprint` fehlt ganz | A1 falsch, edu_robot nutzt anderen Frame-Namen oder keine TF | Mit `ros2 topic echo /odom/wheel --once` `header.frame_id`/`child_frame_id` ansehen. Notfalls rf2o wieder TF veröffentlichen lassen (siehe nächste Zeile) |
| Schritt 3: Karte verschmiert mit Radodometrie | Räder rutschen (A2) | Laser-Odometrie als Quelle: in `pkg_drive/config/edu_robot.yaml` `odometry.publishing_tf: false`, in `pkg_slam/config/slam.launch.py` `publish_tf` von rf2o fest auf `True`, in `nav2_params.yaml` alle `odom_topic: odom/wheel` → `odom/lidar` |
| Schritt 2: zwei Quellen für eine TF | Ein Knoten läuft noch mit alter Konfiguration | `./projectctl.bash down`, neu `build` und `up` |
| Weiterhin `extrapolation into the future` | Odometrie-TF zu selten oder Zeitversatz | `tf2_monitor` zeigt die Verzögerung. `transform_tolerance` in `collision_monitor` erhöhen (z. B. 1.0) oder dort `base_shift_correction: false` |
| `Message Filter dropping message ... earlier than all the data` | Noch eine zweite `map -> odom`-Quelle | Schritt 2 wiederholen, Quelle abschalten |
| Nav2 plant, Roboter bewegt sich nicht | twist_mux/twist_limiter | `ros2 topic echo /cmd_vel/nav` und `/cmd_vel`. Lock `vel_locks/pause_navigation` in twist_mux prüfen |
| Roboter fährt in falsche Richtung | Frame-Achsen / Vorzeichen der Odometrie | Mit Joystick vorwärts fahren und prüfen, ob `/odom/wheel` x positiv wird |

## 7. Offen vor dem Merge nach `main`

- **Testergebnis** der Schritte 1–8 im Pull Request festhalten.
- **Bleibt bewusst drin**: Sams erster Nav2-Versuch (`config/navigation.launch.py`,
  `config/parameters/`, `georg_slam.rviz`) als Referenz, die Aufnahme
  `pkg_viz/config/odomtest` (~30 MB) für die Sensorfusion und die Skip-Liste in
  `projectctl.bash` (`speech`, `examples`, `task_manager`).
- **Simulation**: Nav2 ist hier nur für den Roboter eingestellt (kein Sim-Modus). Die
  Simulation mit Nav2 läuft bisher nur auf `pkg_task_manager_burr`.

## 8. Später: Sensorfusion

Entscheidung für jetzt: Radodometrie, damit der Test wenige bewegliche Teile hat. Später
sollen Laser, Räder und IMU zusammen die Odometrie liefern, damit rutschende Räder kaum noch
stören.

Zahlen aus Sams Aufnahme `odomtest` (11 Minuten am Roboter, `pkg_viz/config/odomtest`),
Schritt für Schritt verglichen mit der Pose von SLAM:

| | Rad | Laser |
|---|---|---|
| Positionsfehler je Schritt, Median | 27 cm | 12 cm |
| Drehfehler je Schritt, Median | 1,3° | 0,5° |

Der Vergleich ist nicht ganz fair, weil SLAM selbst den Scan nutzt und in der Aufnahme nicht
stabil war.

Laser-Odometrie ist schwach in langen glatten Fluren, großen offenen Flächen, bei vielen
Menschen um den Roboter, bei Glas/Spiegeln und bei schnellen Drehungen. Dann springt sie eher,
statt langsam zu driften. Räder driften dagegen schleichend durch Rutschen.

Umsetzung:

- `robot_localization` (EKF) bekommt `/odom/lidar`, `/odom/wheel` und `/imu` und
  veröffentlicht als **einzige** Quelle `odom -> base_footprint`. rf2o und edu_robot
  veröffentlichen dann nur noch Topics.
- Gewichtung über die Kovarianzen: Laser hoch, Räder niedriger, IMU hoch für die Drehung.
  Besser Geschwindigkeiten fusionieren als absolute Posen.
- Ausreißer verwerfen über die Mahalanobis-Schwellen von robot_localization: meldet der Laser
  z. B. 1 m in 1 s, während Räder und IMU fast Stillstand zeigen, wird die Messung verworfen.
  Plausibel ist ohnehin nur bis 0,47 m/s (twist_limiter).
- Nav2 liest dann `odometry/filtered` statt `odom/wheel`.
- Einstellen geht ohne Roboter: Die Aufnahme `odomtest` enthält Scan, beide Odometrien und IMU.

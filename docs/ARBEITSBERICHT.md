# Arbeitsbericht Jetson (ab 2026-11-21)

Laufender Bericht zur Umsetzung des Gesamtplans (`docs/HANDOFF.md`). Arbeit auf dem Jetson Thor,
**nicht am Roboter angeschlossen**. Alles nur auf Branch `pkg_task_manager_burr`, `main` bleibt
unverändert, gepusht wird nur nach Rückfrage. Kein Profil `real`, keine Befehle an Hardware.

Format je Entscheidung: **Problem** – **Optionen** – **Gewählt** – **Folgen**.

## Bereits erledigt (vor diesem Bericht, mit dir abgestimmt)

| Commit | Was |
| --- | --- |
| `0546a8b` | Merge `origin/main` (Sams `sim_mode`, Namespace aus) in unseren Branch |
| `5fdf9c0` | Kein Robot-Namespace mehr, Services heißen `/task_manager/start` usw. |
| `12894fe` | Docker-Build auf arm64: `apt-get update` vor `rosdep`, `pib-sdk` nicht mehr im Gesten-Image |
| `15cd31e` | `command_gate` entfernt, `ROS_DOMAIN_ID` real = 0, sonst 30 |
| `68fd5d7` | Domain-Brücke zu pib-backend für Phase 5 vorgemerkt |

Auf dem Jetson: alte Container `georg-drive-1`/`georg-urdf-1` gestoppt (`restart=no`), alte Images
als `:pre-jetson-20261121` gesichert, alte `georg-*`-Container durch neue ersetzt (mit OK).

## Entscheidungen

### E1 – Phase 5 (Sprache) wird mitgemacht
- **Problem:** Phase 5 war „erst auf Ansage“. Neue Anweisung: „arbeite alles einfach ohne Pause durch“.
- **Optionen:** (a) Phase 5 weiter auslassen, (b) mitmachen.
- **Gewählt:** (b), weil direkt davor über den Speak-Port gesprochen wurde.
- **Folgen:** Task Manager bekommt `Speak`/Listening über pib-backend; unser `datatypes` fällt weg.
  Falls das nicht gewollt war: Phase-5-Commits lassen sich einzeln zurücknehmen (`git revert`).

## Verlauf

### Phase 2 – Docker auf dem Jetson
- Alle 12 Images bauen (arm64).
- `up mock`: alle Dienste `healthy`, Domain 30 in allen Containern.
- Mission `mock_test` per `ros2 service call /task_manager/start`: Listening → Gesture →
  NavigateObject → ReturnToIdle → **succeeded** (1,7 s).
- ROS-Tests im Container (`task_manager`-Image, arm64): Unit (Burr 18, Validator 27,
  Planer 17), Mock-Integration **10/10**, LLM-Integration **9/9**.
- `up sim`: alle Dienste `healthy`, echte Gesten- und Navigationsserver laufen.

### Fehler gefunden und behoben: Simulator lief noch im Namespace `georg`
- **Problem:** Erste Sim-Mission scheiterte sofort. `pkg_sim/docker-compose.yaml` startete den
  Simulator mit `-r __ns:=/georg`; beim Namespace-Commit übersehen (mein Suchfilter blendete
  Zeilen mit `georg_sim` aus). Der Healthcheck merkte es nicht, weil `/georg/georg_sim` auch auf
  `/georg_sim$` passt.
- **Gewählt:** Remap entfernt; alle Healthchecks prüfen den Namen jetzt exakt (`grep -qx`).
- **Folgen:** Healthchecks setzen „kein Namespace“ voraus. Wer `EDU_ROBOT_NAMESPACE=georg` setzt,
  bekommt `unhealthy` – das ist gewollt, weil der Stack dann ohnehin nicht zusammenpasst.

Comment: das müssen wir später mal ausbessern so finde ich das blöd
> Antwort: notiert unter „Später“ (S1). Nebenbei: `EDU_ROBOT_NAMESPACE` kommt heute gar nicht
> in die Container (Compose reicht die Variable nicht durch) – der Schalter wirkt also nur halb.
> Sauber wäre: Variable an alle Dienste durchreichen und Healthchecks daraus bauen.

### E2 – Wie Sim-, MCAP- und Lichtblick-Tests im Container laufen
- **Problem:** Diese pytest-Tests starten Task Manager, Simulator, Navigation, SLAM und
  `foxglove_bridge` in **einer** ROS-Umgebung. Auf dem Mac ging das (ein Workspace), in Docker
  liegt jedes Paket in einem eigenen Image.
- **Optionen:**
  (a) eigenes Test-Image, das alle Pakete zusammenführt – nah an den Mac-Tests, aber ein
  zusätzliches großes Image, das gepflegt werden muss und nicht dem Roboter entspricht;
  (b) Abnahme gegen den laufenden Compose-Stack – testet genau das, was auf dem Roboter läuft
  (Container, Netz, Healthchecks, Domain), braucht aber einen laufenden Stack;
  (c) diese Tests nur auf dem Mac lassen.
- **Gewählt:** (b), neu `tests/stack/run.sh mock|sim` (`stack_check.py`). Die Mac-Tests bleiben
  unverändert.
- **Folgen:** Im Container geprüft wird das Verhalten (Mission, Karte, Ankunft, Abbruch), nicht
  jeder einzelne pytest-Fall. MCAP-Replay und Lichtblick-Brücke prüfe ich in Phase 6 einzeln.
  `run.sh sim` startet Simulator und SLAM neu, damit Georg am Startpunkt steht.
- **Ergebnis Sim:** 6/6 – Missionsliste, Ablehnung mit Grund, `/odom`, SLAM-Karte,
  `sim_seat` fährt 4,76 m und endet 0,38 m vor dem Sitzplatz, Abbruch stoppt sofort.
  Der Test prüft die **Pose**, nicht nur den Status – wegen Q21 meldet eine Mission auch dann
  `succeeded`, wenn die Fahrt scheiterte.

  Comment: ja das müssen wir noch irgendwie besser aufräumen oder irgendwie weil so ist bissl dumm maybe eigene branches kp
  > Antwort: notiert unter „Später“ (S2). Vorschlag dort.

### Fund (nicht behoben, fremdes Paket): Q33 – nach Abbruch in der Engstelle kein Weiterkommen
- Abbruch mitten in der 0,55-m-Lücke (Q25) → Georg steht in einer Sicherheitszelle → der Planer
  lehnt jedes Ziel ab. Vorher 13 s gleicher Fahrbefehl ohne Fortschritt (keine
  Steckenbleib-Erkennung). Gemeldet in `docs/OPEN_QUESTIONS.md` Q33.
- **Folge für uns:** Nach einem Abbruch kann eine Sim-Session „hängen“; abhilfe heute:
  `tests/stack/run.sh sim` bzw. Simulator neu starten. Auf dem Roboter wäre das ein echtes
  Problem → wichtig für die Navigation.

Comment: Ja das müssen wir definitiv angehen 

### Phase 3 – Georg komplett in Lichtblick (neues Paket `pkg_pib_model`)

#### E3 – Welches pib-Modell
- **Optionen:** (a) offizielles `pib.urdf` von pib-3d (351 Links, Einzelteil-Meshes, allein der
  Brustkorb 7,8 MB); (b) Web-Modell aus dem pib-3d-Release (`model.json`, 47 Links, ein GLB je
  Link – das, was Cerebra zeigt), selbst nach URDF umwandeln; (c) pib-sdk-URDF (nur Kinematik).
- **Gewählt:** (b). Gleiche Quelle und Version wie Cerebra (`v0.11.6`, SHA-256 aus pib-backend),
  sinnvoll schwer, Umrechnung der Gelenkwinkel identisch zu Cerebra.
- **Folgen:** Das Modell wird **beim Image-Build aus dem Netz geladen** (GitHub-Release), nicht
  ins Repo kopiert. Grund: Lizenz unklar (Repo AGPL-3.0, `package.xml` „Proprietary“) –
  **bitte klären, bevor Images weitergegeben werden.** Ohne Internet beim Build kein Modell.

  Comment:  erkläre verstehe garnicht erstens warum eigener container und dnicht mit der fahrenden bas e in einen und 2 tens warum nicht das urdf direkt klingt doch ansich besser und einfacher

#### E4 – Wie die Meshes zu Lichtblick kommen
- **Fund:** Das Bridge-Image enthielt bisher **kein** `georg_description` → in Docker hätte
  Lichtblick Georg ohne Meshes gezeigt (auf dem Mac fiel das nicht auf). Außerdem lässt die
  Standard-Freigabeliste der Bridge keine Leerzeichen zu → `Mecanum Wheel.obj` wäre blockiert.
- **Optionen:** (a) Meshes aus den Images `urdf`/`pib_model` in die Bridge kopieren (hängt von
  Build-Reihenfolge und Profilen ab); (b) Bridge lädt/klont selbst.
- **Gewählt:** (b): Bridge klont `georg_description` (wie `pkg_urdf`) und lädt das pib-Modell
  (gleiche Pinnung). Freigabeliste mit Leerzeichen in `pkg_viz/config/foxglove_bridge.yaml`.
- **Folgen:** Modell wird zweimal geladen (15 MB, Sekunden). `georg_description` in Bridge und
  `urdf` sind beide „main“ zum Build-Zeitpunkt – bei Änderungen beide neu bauen.

 Comment: auch das müssen wir nochmal besprechen

#### E5 – Starres pib-Mesh von Georg und Montage
- **Problem:** `georg_description` zeigt pib als ein starres `pib_4S.stl`; doppelt mit dem
  beweglichen pib sähe es falsch aus. `pkg_urdf` soll unverändert bleiben.
- **Gewählt:** `pib_model_node` baut aus Georgs `/robot_description` eine zweite Beschreibung
  `/georg_full/robot_description` (ohne `pib_4S.stl`, mit pib); das Layout zeigt nur diese.
  Montage `pib_waist_link → root`: +90° um z, (0,103 | 0,065 | 0,613) m, **geschätzt** aus den
  Bounding-Boxen (Kopfoberkante, Schulterhöhe). Parameter `mount_xyz`/`mount_rpy`.
- **Folgen:** Wer ein eigenes Layout nutzt, sieht sonst beide pibs. **Die Montage bitte in
  Lichtblick ansehen** – ich kann das Bild nicht sehen.

#### Ergebnis (im Stack, Profil `sim`)
- `pib_model` healthy; kombinierte Beschreibung ohne starren STL; tf `base_footprint →
  d01_l_palm_left` (Hand links auf 1,45 m); Ellbogen links 60° über die Fake-Motoren →
  URDF 1,047 rad, Hand bewegt sich 0,24 m, zurück auf 0 exakt.
- Bridge liefert alle Meshes (`root.glb` 9,1 MB, `Basis.obj`, `Mecanum Wheel.obj`, Lidar-DAE).
- 7 Unit-Tests (Umwandlung, Winkelformel, Kopplung, Kombination), inkl. echtem `mapping.json`.
- **Offen:** ~50 MB Meshes beim ersten Verbinden – Verkleinern als eigener Schritt (Phase 6).

#### Fund (nicht behoben, fremdes Paket): Q34 – Gesten bewegen nichts
- Gesten-Server meldet Erfolg, sendet aber keinen Gelenkbefehl (pib-sdk auskommentiert).
  Vorschlag: `/apply_joint_trajectory` von pib-backend nutzen – dann sieht man die Gesten sofort
  in der Sim (Fake-Motoren) und auf dem Roboter.

  Comment: muss dringend behoben werden 

### Phase 4 – Fahren in der Sim wie am Roboter

#### E6 – Wie weit Sams `sim_mode` in der Sim geht
- **Problem:** Ganz auf `sim_mode` umzustellen hieße: `rf2o` macht die Odometrie, `odom` beginnt
  am Startpunkt bei (0, 0). Die Navigation rechnet aber `Karte = odom + fester Versatz aus der
  Karten-YAML` und nutzt die SLAM-Pose nicht (Q36) – sie läge um die Startpose daneben.
  Außerdem sendet Sams SLAM-Launch `map → odom` doppelt (Q35).
- **Optionen:** (a) alles umstellen und Navigation/SLAM in der Sim kaputt machen; (b) nur den
  Fahrpfad umstellen, SLAM/Odometrie bleiben bei der Sim-Lösung; (c) gar nichts umstellen.
- **Gewählt:** (b). In `sim` läuft `pkg_drive` mit `sim_mode` (twist_mux + twist_limiter, **ohne**
  Treiber `edu_robot`), Navigation fährt über `cmd_vel/nav` – genau die Kette des Roboters.
- **Folgen:** Die doppelte SLAM-Lösung (Q30) bleibt, bis die Navigation die Lokalisierung löst
  (Q36) und Sam Q35 behebt. Dann: Simulator ohne odom-tf, `rf2o` an, `slam_sim.launch.py` weg.
  `projectctl` setzt `GEORG_SIM_MODE` **nur** aus dem Profil (nie aus deiner Shell): `real`
  startet immer den Treiber, `sim` nie. Der `drive`-Container läuft in `sim` jetzt mit
  `privileged` und `/dev` (so ist Sams Compose) – der Treiber startet dort aber nicht.

Comment auch das müssen wir besprechen 

#### Fehler gefunden und behoben
- **QoS:** `twist_limiter` sendet `cmd_vel` als *best effort*, der Simulator abonnierte
  *reliable* → **keine einzige Nachricht** kam an, Georg stand still. Simulator abonniert jetzt
  best effort (verträgt beides). Am Roboter betrifft das nur, falls ein Node `cmd_vel` reliable
  abonniert.
- **Doppelte tf:** Simulator sendete `base_footprint → base_link` mit 0 m, `georg_description`
  mit 0,128 m – im Stack jetzt nur noch das URDF.
  

#### Realistischere Sensoren (Parameter des Simulators, Schalter im Compose)
| Parameter | Standard im Stack | Was |
| --- | --- | --- |
| `GEORG_SIM_LIDARS` | `robot` | zwei TiM571 an den URDF-Positionen, 270°, → `lidar1/scan`, `lidar2/scan`, `merged_scan` wie der Scan-Merger (1°, ab 0,3 m) |
| `GEORG_SIM_LIDAR_NOISE` | `0.02` m | Gauß-Rauschen pro Strahl |
| `GEORG_SIM_ODOM_NOISE` | `0` | relatives Geschwindigkeitsrauschen → Drift von `odom`/`odom/wheel` |
| `GEORG_SIM_CMD_LATENCY` | `0` s | Befehle wirken verzögert |

Dazu `/clock` (für `use_sim_time` in `pkg_drive`) und `sim/ground_truth` (wahre Pose, nur Tests).
Strahlauflösung 1° statt 0,33°: der zusammengeführte Scan hat ohnehin 1°, Python-Raycasting mit
0,33° wäre auf dem Jetson zu langsam.

#### Ergebnis
- Stack-Test `sim` **6/6** mit sim2d **und** mit MuJoCo (Fahrpfad über twist_mux/limiter, zwei
  Lidare mit Rauschen, SLAM-Karte aus dem zusammengeführten Scan).
- Mit 5 % Odometrie-Rauschen ebenfalls 6/6 – zufälliges Rauschen mittelt sich weg; echter
  Schlupf ist eher systematisch. Systematischen Fehler (z. B. 3 % zu kurz) könnte man als
  weiteren Parameter ergänzen.
- `tests/system` 8/8 (Treiber-Test angepasst: in `sim` nur mit `sim_mode:=true`).
- Gemeldet: Q35 (SLAM `map → odom` doppelt), Q36 (keine Lokalisierung in der Karte).

## Später (vereinbart bzw. aus deinen Kommentaren)
- **S1 – Namespace sauber machen:** `EDU_ROBOT_NAMESPACE` an alle Dienste durchreichen,
  Healthchecks daraus bilden (heute fest „kein Namespace“).
- **S2 – Tests aufräumen:** Mac-pytest (ein Workspace) und Stack-Test (Container) prüfen
  teilweise dasselbe auf zwei Wegen. Vorschlag: Die Integrationstests werden zu Stack-Tests
  (laufen gegen `projectctl up`, auf Mac mit Docker ebenso), die Mac-pixi-Tests bleiben nur
  für schnelle Unit-Tests. Eigene Branches dafür sind nicht nötig – ein Ordner `tests/stack`
  als einziger Integrationsweg reicht.
- **S3 – Meshes verkleinern** (~50 MB beim ersten Verbinden von Lichtblick).
- **S4 – Q21:** Mission meldet `succeeded`, obwohl ein LOW-Task scheiterte.

### Phase 5 – Sprache über pib-backend (Schritt 1 von 2: Task Manager) – erledigt

#### E7 – Namenskonflikt `datatypes` und Anbindung an pib-backend
- **Problem:** Unser Paket `datatypes` (Listen, VoiceEvent, VoiceTask, aus `pib-audio`) und das
  `datatypes` von pib-backend (PlayAudioFromSpeech, ApplyJointTrajectory, …) heißen gleich,
  sind aber verschieden. pib-backend hat **keine** `Listen`-Action und keine Türklingel.
- **Optionen:** (a) unser Paket löschen, Task Manager direkt auf pib-backend umbauen (Listening
  auf `/speech_detected`/`/chat_messages`, Speak als Service-Aufruf); (b) unser Paket
  umbenennen, Task Manager behält seinen Vertrag (Actions), ein kleiner Adapter übersetzt zu
  pib-backend.
- **Gewählt:** (b). Unser Paket heißt jetzt `georg_speech_msgs` (dazu neu `Say.action`); das
  Basis-Image baut zusätzlich `datatypes` aus dem pib-backend-Repo, gepinnt auf den Commit, der
  auf dem Jetson läuft (`f3a8a376`, v0.7.10).
- **Folgen:** Task Manager und Mocks hängen nicht an pib-backend-Details; wenn pib-backend seine
  Schnittstellen ändert, muss nur der Adapter (Schritt 2) angepasst werden. Neue
  pib-backend-Version → Pinnung im Basis-Image mitziehen.

#### E8 – Speak als Action statt Service
- **Problem:** Der Branch `pib_backend_integration` ruft `/play_audio_from_speech` direkt als
  Service auf. Katalog, Startprüfung, Mocks und Abbrechen kennen nur Actions.
- **Gewählt:** Task `Speak` nutzt die Action `speech/say` (`georg_speech_msgs/Say`); der Adapter
  ruft dahinter den Service. Text, Stimme (`M1`, `de`) und Mission „Greeting“ wie im Branch.
- **Folgen:** `Speak` lässt sich abbrechen und erscheint im Katalog (auch für das LLM).

#### Ergebnis
- Im Container: Burr 18, Validator 27, Planer 17, Mock-Integration 10/10.
- Stack `mock`: 4/4, neue Mission `greeting` spricht zweimal über `speech/say` (Mocks).
- **Noch offen (Schritt 2):** Adapter `pkg_pib_bridge` – `speech/say` → pib-backend
  `/play_audio_from_speech`, `audio/listen` (SPEECH) → `/speech_detected` + `/chat_messages`,
  Brücke zwischen Domain 30 (Sim) und 0 (pib-backend), Türklingel ohne Quelle (Frage).

### Nach dem Durchgehen – Lichtblick-Darstellung, Reset, Gesten-Demo

#### Fehler gefunden und behoben
- **pib-Meshes fehlten:** URDF zeigte auf `package://pib_model/meshes/…`, installiert ist
  `…/model/meshes/…` (mein Fehler; der frühere Bridge-Test nutzte den richtigen Pfad von Hand).
  Neu: `tests/stack/mesh_check.py` lädt **jede** URI aus den Beschreibungen über die Bridge (52/52).
- **Gekippte Basis/Beine/Lidare/pib:** keine Modellfehler. Lichtblick behandelt STL/OBJ/GLB
  standardmäßig als „y oben“ und wendet COLLADA-`<up_axis>` an; alle Meshes von Georg und pib
  liegen aber in ROS-Ausrichtung (z oben). Lösung: 3D-Panel → Scene → **Mesh up axis = Z-up**,
  **Ignore COLLADA up_axis** an – jetzt im Layout `georg_sim.json` (dazu Labels/Achsen aus,
  URDF-Ebene „Georg + pib“). **Korrektur:** „Mesh up axis“ gilt nur für STL/OBJ – GLB dreht
  Lichtblick immer um +90° um x. Die pib-Meshes behalten deshalb ihre Gegendrehung (−90° um x);
  ohne sie flog der Oberkörper auseinander (Explosionsansicht). Kurz entfernt, weil ich deine
  Rückmeldung falsch gedeutet hatte, dann wieder eingebaut.
- Lichtblick erkennt nur `/robot_description` von selbst als Roboter; das kombinierte Modell kommt
  über die Custom-URDF-Ebene (Topic `/georg_full/robot_description`).

#### Reset für die Sim (Wunsch)
- Mission **„Simulation: zurücksetzen“** (`sim_reset`), nur Profil `sim`: Georg an den Start,
  gestoppt, Odometrie zurück, SLAM-Karte leer (`/slam_toolbox/reset`), bei MuJoCo auch der
  Physikzustand. Neu: `georg_sim_msgs/ResetSim`, Action `sim/reset` im Simulator.

#### E9 – Gesten sichtbar machen
- **Problem:** Der Gesten-Server bewegt nichts (Q34). Wunsch: eine Mission, in der man Gesten sieht.
- **Optionen:** (a) Gesten-Paket umbauen (fremdes Paket, Sache des Gesten-Teams); (b) eigener
  Task für benannte Posen, in der Sim von den Fake-Motoren ausgeführt.
- **Gewählt:** (b). Task `pib_pose` (Action `pib/pose`, `georg_gesture_msgs/PibPose`), Posen
  `ruhe`, `winken`, `zeigen`, `begruessen`, `arm_hoch`, `kopf_mitte` in
  `pkg_pib_model/config/pib_poses.yaml` (ohne Neubau änderbar). Mission **„Simulation:
  Gesten-Demo“** (`sim_gestures`): winken → Sitzplatz → zeigen → begrüßen → Arme runter.
- **Folgen:** Die Winkel sind über die Kinematik des Modells aus Ziel-Handpositionen berechnet,
  **nicht am echten pib geprüft**, teils an der Grenze ±1,5 rad → Task nur `mock`/`sim`. Für
  `real` später: Adapter → pib-backend `/apply_joint_trajectory`, Posen vorher am Roboter prüfen.
  Die Fake-Motoren bieten jetzt auch `/apply_joint_trajectory` an (wie pib-backend), weil dessen
  `datatypes` im Basis-Image ist – das Gesten-Team kann seine Ansteuerung damit in der Sim testen.

#### Ergebnis
- Stack-Test `sim` **8/8** (inkl. Reset und Gesten-Demo), `mock` 4/4; Unit-Tests grün.

### Phase 5 – Schritt 2: Adapter `pkg_pib_bridge`
- Ein Prozess in zwei ROS-Domains (Stack 30, pib-backend 0), einziger Container in beiden
  Docker-Netzen, optional per `GEORG_WITH_PIB_BACKEND=1`. Freigabeliste: `speech/say` →
  `/play_audio_from_speech`; `audio/listen` → `/speech_detected` + `/chat_messages`; Kopfkamera
  und Erkennungen nur lesend. Keine Motor- oder Fahrbefehle.
- **E10 – zwei Domains in einem Prozess statt `domain_bridge`:** `domain_bridge` hätte Topics
  generisch gebrückt; für Speak/Listen braucht es aber Logik (Action ↔ Service, Ereignis →
  Ergebnis). Ein eigener Node mit zwei rclpy-Kontexten macht beides und hält die Freigabeliste im
  Code. Folge: neue Topics brauchen einen Eintrag in `forward_topics`.
- **Ergebnis (Jetson, pib-backend läuft hier):** Kamerabild der echten OAK-Kamera kommt im Stack
  an (9,7 Hz, JPEG) → in Lichtblick als Image-Panel `/oak/rgb/image_raw/compressed`.
  `audio/listen` meldet ohne Sprache nach Ablauf korrekt „nicht erkannt“.
  `speech/say` erreicht pib-backend, aber dessen `audio_player` antwortet nicht (Q37, kein
  Lautsprecher, JACK fehlt) – auch bei Aufrufen aus pib-backend selbst.
- **Am Schluss ausbessern:** Netz am echten Roboter (pib-backend auf dem Pi), Türklingel-Quelle,
  Kamera-Frame am pib-Kopf, Speak-Test mit Lautsprecher.

### Phase 6 – Gesamttest (Jetson, 2026-11-21 abends)

| Prüfung | Ergebnis |
| --- | --- |
| `tests/system` | 8/8 |
| Unit-Tests im Container (Burr, Validator, Planer) | 18 / 27 / 17 grün |
| ROS-Integration im Container (Mock, LLM) | 10/10, 9/9 (Stand Phase 2; danach nur Unit-Tests wiederholt) |
| Stack `mock` (`tests/stack/run.sh mock`) | 4/4 |
| Stack `sim` mit pib-backend-Brücke (`run.sh sim`) | 8/8: Navigation, Abbruch, Reset, Gesten-Demo |
| Meshes über die Bridge (`mesh_check.py`) | 52/52 |
| Profil `mcap` (neu in Docker) | Sim-Fahrt mit Sensoren aufgenommen (44 s, `recordings/sim_drive_jetson`), abgespielt, SLAM baut daraus die Karte (170×84) |
| Brücke zu pib-backend | Kamera 9,7 Hz im Stack; Listen korrekt; Speak hängt an pib-backend (Q37) |

## Am Schluss ausbessern (gesammelt)
1. **Vorne bei Georg klären** – starrer pib in `georg_description` und Navigation
   (`FRONT_YAW_OFFSET`) passen evtl. nicht; danach Montage-Gier des beweglichen pib anpassen.
2. **pib-backend Sprachausgabe** (Q37): Container `pib-backend-ros-voice-assistant-1` neu starten
   (deine Zustimmung nötig), Lautsprecher anschließen, Speak erneut testen.
3. **Lizenz des pib-Modells** klären (AGPL vs. „Proprietary“), bevor Images weitergegeben werden.
4. **Posen** (`pib_poses.yaml`) am echten pib prüfen, erst dann `pib_pose` für `real` freigeben.
5. **Netz am echten Roboter:** pib-backend auf dem Pi im LAN → Brücke braucht Zugang zum
   Roboternetz (Host-Netz oder macvlan); ebenso sieht `pib_model` sonst keine echten Gelenkwinkel.
6. **Kamera:** Frame am pib-Kopf, Sim-Kamera (MuJoCo EGL) mit Arena und Personen, Erkennungen in
   der Sim aus bekannten Positionen.
7. **MuJoCo:** Georg-Mesh statt Zylinder.
8. **S1** Namespace sauber (Variable durchreichen, Healthchecks), **S2** Tests aufräumen,
   **S3** Meshes verkleinern (~50 MB), **S4** Q21 (Mission „succeeded“ trotz gescheitertem Task).
9. **Fremde Pakete** (gemeldet): Q31/Q36 Navigation/Lokalisierung (wichtigster Punkt vor `real`),
   Q33 Engstelle, Q34 Gesten, Q35 SLAM `map → odom`, Hardware-Scan (12 Probleme).
10. Türklingel-Quelle (evtl. Home Assistant), `projectctl build` meldet bei Fehlern Exit 0.

### Nachtrag: Branch `pib_backend_integration` erweitert (leakmpf, 2 Commits) – eingebaut
- **Zuhören:** neu über die pib-backend-Action `/record_audio` (`RecordAudio`: wartet auf
  Sprechbeginn, endet nach 1 s Pause, Speech-to-Text). Eingebaut in der Brücke: `audio/listen`
  SPEECH ruft jetzt `/record_audio` (vorher mein Umweg über `/speech_detected` +
  `/chat_messages`, entfernt). Task Manager unverändert über `Listening` (Text in `transcript`),
  Listening merkt sich den Text (`.text`, `state.last_heard_text`).
- **Speak mit Text aus dem Zustand** (Funktion statt String), Burr-UI zeigt dafür einen Hinweis
  statt `<function …>`.
- **Greeting:** Begrüßung → „Wie ist dein Name?“ → zuhören → „Schön, dich kennenzulernen
  \<Name>!“ mit `extract_name` aus dem Branch. 8 neue Unit-Tests (Namenserkennung, Text).
- **Getestet:** Mock-Stack 4/4 (Greeting mit Listening). Am Jetson über die Brücke: Aufnahme bei
  pib-backend läuft, Whisper erkennt lokal in 166 ms; ohne Sprecher korrekt „nichts erkannt“.
  Sprechen weiter durch Q37 blockiert.

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

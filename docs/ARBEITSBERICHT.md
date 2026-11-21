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

### Fund (nicht behoben, fremdes Paket): Q33 – nach Abbruch in der Engstelle kein Weiterkommen
- Abbruch mitten in der 0,55-m-Lücke (Q25) → Georg steht in einer Sicherheitszelle → der Planer
  lehnt jedes Ziel ab. Vorher 13 s gleicher Fahrbefehl ohne Fortschritt (keine
  Steckenbleib-Erkennung). Gemeldet in `docs/OPEN_QUESTIONS.md` Q33.
- **Folge für uns:** Nach einem Abbruch kann eine Sim-Session „hängen“; abhilfe heute:
  `tests/stack/run.sh sim` bzw. Simulator neu starten. Auf dem Roboter wäre das ein echtes
  Problem → wichtig für die Navigation.

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

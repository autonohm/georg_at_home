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

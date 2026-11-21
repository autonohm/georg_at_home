# P8 – Georg im Dauerbetrieb auf dem Jetson einrichten

Diese Anleitung bringt die Software auf den Jetson Thor, sodass Georg nach dem Einschalten
von selbst startet, in **Idle** steht und abgestürzte Container von allein wieder hochkommen.

> **Vorab, wichtig:** Das Profil `real` ist gesperrt, solange der Hardware-Scan (P7)
> Probleme findet. Stand 2026-11-21 sind es 13, alle in Paketen anderer Verantwortlicher
> (Abschnitt 1). Bis sie behoben sind, schlägt der Start mit `real` absichtlich fehl,
> und es bewegt sich nichts.

## 1. Freigabe für `real` herstellen (Hardware-Scan)

```bash
python3 tools/hardware_scan.py           # schreibt docs/hardware_access_report.md
python3 tools/hardware_scan.py --check   # Exit-Code 1, solange es Probleme gibt
```

Offene Probleme laut Bericht (Abschnitt „Meldungen an die Paket-Verantwortlichen“):

| Paket | Was zu tun ist |
| --- | --- |
| `pkg_gestures` | `pib-sdk` steuert die Servos des pib per rosbridge am `command_gate` vorbei. Servobefehle über ROS-Topics hinter einem Gate führen, erst dann die SDK-Aufrufe aktivieren. |
| `pkg_slam` | `privileged: true` und `/dev:/dev` entfernen (Lidar läuft über Netzwerk). |
| `pkg_viz` | `/dev:/dev` und `privileged` auf das Nötige für die GPU einschränken. |
| `pkg_urdf`, `pkg_examples` | `privileged: true` entfernen. |

Zusätzlich „offen“ (nicht im Repo prüfbar): beim Bauen geklonter Code, vor allem der
Fahrtreiber `edu_robot`. Prüfen, dass er Fahrbefehle auf `cmd_vel` abonniert. Nur dann greift
die Umleitung auf `cmd_vel/gated` hinter dem `command_gate` (`pkg_drive/config/drive.launch.py`).

Nach jeder Korrektur den Scan erneut laufen lassen. Erst wenn `--check` mit 0 endet,
startet `projectctl.bash up real`.

## 2. Voraussetzungen auf dem Jetson

- Jetson Thor mit JetPack (Ubuntu), Netzwerk im Roboternetz `192.168.2.0/24`
- Docker mit Compose-Plugin. JetPack bringt Docker meist mit. Prüfen mit
  `docker compose version`. Der Docker-Teil in `setup-robot.sh` ist für Debian geschrieben.
  Ist Docker schon da, überspringt das Skript ihn.
- Mindestens 40 GB frei für die Images (Task Manager mit TensorFlow ist groß)
- Optional für das LLM (P6): ein GGUF-Modell in `~/georg-llm` (siehe `packages/pkg_llm/README.md`)

## 3. Einrichten

```bash
mkdir -p ~/app && cd ~/app
git clone https://github.com/autonohm/georg_at_home.git
cd georg_at_home/system-files
./setup-robot.sh
```

`setup-robot.sh` erledigt:

| Schritt | Ergebnis |
| --- | --- |
| udev-Regeln | Joystick `/dev/georg_controller`, Motor-Controller `ttyMotor*` |
| Modusdatei | `/etc/georg/mode` = `real` (nur der Roboter darf `real`) |
| systemd | `/etc/systemd/system/georg.service`, aktiviert (Pfad und Benutzer eingesetzt) |
| Bash | Autovervollständigung für `projectctl.bash` |
| Docker | nur falls nicht installiert; Benutzer in die Gruppe `docker` |

Danach einmal ab- und wieder anmelden, damit die Gruppe `docker` gilt.

## 4. Bauen

```bash
cd ~/app/georg_at_home
./projectctl.bash build real        # Basis-Image (mit pkg_interfaces) + alle Images von real
```

Das dauert beim ersten Mal lange. Ohne Fehler ist das P0-Kriterium „alle Pakete bauen“
auch im Container erfüllt.

## 5. Starten und prüfen

```bash
sudo systemctl start georg          # oder: ./projectctl.bash up real
./projectctl.bash status            # Container mit Zustand (healthy / starting / unhealthy)
./projectctl.bash logs task_manager
```

- **Lichtblick (PC):** Datenquelle *Foxglove WebSocket* `ws://jetson:8765`, Panel
  *Georg Task Manager* (`packages/pkg_viz/lichtblick_panel`, `python3 build.py`, `.foxe` installieren)
- **Burr-UI:** `http://jetson:7241`
- **Aufnahmen:** `recordings/` im Repo (MCAP von `/georg/task_manager/*`, LLM-Entscheidungen
  in `recordings/decisions/`)

## 6. Abnahme P8

| Kriterium | So prüfen | Erwartung |
| --- | --- | --- |
| Nach dem Einschalten steht Georg in Idle | `sudo reboot`, dann in Lichtblick den Status ansehen | Status `IDLE`, Modus `mission`; keine Mission läuft, nichts bewegt sich |
| Ein abgestürzter Container kommt allein wieder hoch | `docker exec georg-task_manager-1 pkill -f task_manager.launch`, dann `./projectctl.bash status` | Container startet neu, nach ca. 1 min `healthy` |
| `up real` wird auf dem PC verweigert | auf dem PC: `./projectctl.bash up real` | Abbruch mit „only runs on the robot“ |

Hinweis zum Absturztest: `docker stop` oder `docker kill` gelten als gewolltes Anhalten.
Docker startet den Container dann nicht neu. Für den Test darum den Prozess **im**
Container beenden, wie oben.

Healthchecks zeigen den Zustand an (`projectctl.bash status`). Einen Container, der läuft
aber „unhealthy“ ist, startet Docker nicht von selbst neu. Dann `./projectctl.bash logs <dienst>`
lesen und den Container gezielt neu starten (`docker restart georg-<dienst>-1`).

## 7. Betrieb

| Aufgabe | Befehl |
| --- | --- |
| Status | `./projectctl.bash status` |
| Anhalten | `sudo systemctl stop georg` |
| Nicht mehr beim Booten starten | `sudo systemctl disable georg` |
| Mission starten | Lichtblick-Panel, oder `ros2 service call /georg/task_manager/start georg_task_manager_msgs/srv/StartMission "{mission_id: digital_festival}"` |
| Abbrechen | Panel „Abort“, oder `.../task_manager/cancel` |
| Not-Aus | Hardware-Not-Aus, unabhängig von der Software |

**LLM-Betrieb auf dem Roboter (P6)** bleibt gesperrt, bis die Replay- und Simulationstests
mit dem Modell des Jetsons bestanden sind. Erst dann in der Umgebung des Dienstes
`GEORG_LLM_REAL_APPROVED=1` und `GEORG_WITH_LLM=1` setzen, zum Beispiel in einer Datei
`/etc/systemd/system/georg.service.d/llm.conf` mit `Environment=...`.
Für die ersten Fahrten mit LLM die Betriebsart **LLM + Freigabe** nehmen.

## 8. Fehlersuche

| Symptom | Ursache / Abhilfe |
| --- | --- |
| `georg.service` schlägt beim Booten fehl | `journalctl -u georg`. Meist ist der Hardware-Scan nicht sauber (Abschnitt 1) oder `/etc/georg/mode` steht nicht auf `real`. |
| `StartMission` abgelehnt: „action server not reachable“ | Das genannte Paket läuft nicht: `./projectctl.bash status`, Logs des Pakets |
| Lichtblick verbindet nicht | Lichtblick 1.30.0 verwenden. `foxglove_bridge` 3.x spricht nur `foxglove.sdk.v1`. |
| Roboter fährt nicht in `real` | Fahrbefehle laufen `cmd_vel/nav` → `twist_mux` → `twist_limiter` → `cmd_vel` → `command_gate` → `cmd_vel/gated` → Treiber. `ros2 topic hz` auf jeder Stufe prüfen. Log des Gates: „gate OPEN“ nur, wenn Modusdatei **und** Profil `real` sind. |

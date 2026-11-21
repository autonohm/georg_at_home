# Georg Dahoam

Software für den AutonOhm 'Georg' roboter.

## Plan
Es kommt noch ein Setup-skript um die ganzen container parallel zu bauen, und ein weiteres um systemseitige Software am Hauptcomputer (Jetson Thor) einzustellen.  
Der Pi soll relativ wenig Software ausführen, bzw ein leicht modifiziertes [pib-backend](https://github.com/autonohm/pib-backend).

## docker_base_image
Dieser Ordner baut einen container der als Basis für alle Pakete verwendet wird.  
Darin enthalten sind standard-Pakete und Nachrichten-definitionen.

## packages
Dieser Ordner enthält die Bauanweisungen der einzelnen Subsysteme.  
Die Implementation dieser Sybsysteme kann direkt vorlegen, oder eine Referenz auf ein externes Github repo sein.  


Jedes Subsystem definiert einen eigenen Container, damit dependencies separat gehalten werden.  
Sowie einen `launch-content` Ordner der auf Laufzeit in den container verlinkt wird, und alles enthält was potentiell schnell geändert werden muss (ohne den container neu zu bauen). Z.b. Parameter und Launch files.  
Die Pakete eines Containers werden im Bauprozess kompiliert und ihre dependencies installiert.  
Der Plan ist den container nur bei Softwarerevisionen aktualisieren zu müssen, damit auf dem Roboter eine "production"-Version der Software laufen kann.

### Aufbau eines Subsystems

Jedes Subsystem ist gleich aufgebaut, egal ob es ein oder mehrere ROS-Pakete enthält:

```
packages/pkg_<bereich>/            1 Subsystem = 1 Container
├── README.md
├── Dockerfile, docker-compose.yaml
├── config/                        Launch-Dateien, Parameter (zur Laufzeit gemountet)
└── <paketname>_pkg/               ROS-Paket: package.xml, setup.py | CMakeLists.txt, test/
    └── <paketname>/ | src/ | msg/ srv/ action/
                                   Python-Code | C++ | Nachrichten
```

Beispiel: `packages/pkg_task_manager/task_manager_pkg/task_manager/node.py`

Regeln:

1. **Paketordner = Paketname + `_pkg`** (Paketname wie in `package.xml`), wie in `pkg_navigation`.
   Der Python-Ordner darin heißt genau wie das Paket, das verlangt ROS 2 für Python-Pakete
   (`from task_manager.engine import ...`, `ros2 run task_manager task_manager`).
   So ist auf einen Blick klar: `…_pkg/` = ROS-Paket, Ordner darin = Code.
2. **Die Paketebene bleibt auch bei nur einem Paket.** Container-Dateien (Dockerfile, Compose,
   `config/`) liegen im Subsystem, nicht im ROS-Paket. Weitere Pakete kommen daneben
   (z.B. `pkg_navigation`).
3. **Paketnamen ohne `georg_`**, außer bei Nachrichtenpaketen: `georg_nav_msgs`,
   `georg_task_manager_msgs` usw. brauchen das Präfix, sonst kollidieren sie mit ROS-Standardpaketen
   (`nav_msgs`).

Umgesetzt in `pkg_task_manager` und `pkg_navigation`. Andere Pakete weichen noch ab und werden von
ihren Teams angepasst (z.B. `pkg_sim/georg_sim`).

Nachrichten, die zwischen Containern gebraucht werden, liegen in `pkg_interfaces` und werden ins
Basis-Image gebaut. Eine leere Datei `PKG_IGNORE` nimmt ein Subsystem aus dem Bauen/Starten heraus.

## IP Addressen
Es gibt einen DHCP server.  
Jedoch benötigen viele Teilnehmer statische Addressen.  

- Alle Addressen sind im Subnet `192.168.2.0/24` unterbracht.  
- Subsysteme können durch pingen überprüft werden.
- Alle IPs haben DNS resolving: Namen können verwendet werden.  
  (entweder nur mit Namen `ping jetson` oder mit voller Domain `ping jetson.georg.net`)

### Übersicht
| IP Bereich            | Verwendung                               | Typ    |
|-----------------------|------------------------------------------|--------|
| 192.168.2.1 - ".20    | Physikalische Hardware                   | Static |
| 192.168.2.21 - ".50   | Container auf dem Pib                    | Static |
| 192.168.2.51 - ".80   | Container auf dem Jetson                 | Static |
| 192.168.2.100 - ".255 | Externe physikalische Hardware (Laptops) | DHCP   |


### Detail
<details>

<summary>Vollständige Liste der IP addressen</summary>

| IP   | DNS                | Verwendung                                                     |
|------|--------------------|----------------------------------------------------------------|
| ".1  | raspi              | Raspi auf dem Pib                                              |
| ".2  | jetson             | Jetson thor                                                    |
| ".20 | edu-motor-board    | EduArt Ethernet→CAN Motorcontroller adapter                    |
| ".21 | pib-rosbridge      | rosbridge (ROS→HTTP) container am Pib                          |
| ".22 | pib-flask          | Flask API container am Pib                                     |
| ".23 | pib-blockly        | Blockly server (blockbasiertes Programmieren) container am Pib |
| ".24 | pib-camera         | Luxonis Kamera Node container am Pib                           |
| ".25 | pib-motors         | Servomotor Steuerung Node container am Pib                     |
| ".26 | pib-webots         | Webots Simulator container am Pib                              |
| ".27 | pib-voiceassistant | Voice assistant container am Pib                               |
| ".28 | pib-ros-programs   | Cerebra Programme container am Pib                             |
| ".29 | pib-display        | Display container am Pib                                       |
| ".30 | pib-audio-io       | Audio I/O container am Pib                                     |
| ".40 | pib-cerebra        | Cerebra Webserver container am Pib                             |

</details>

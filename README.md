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

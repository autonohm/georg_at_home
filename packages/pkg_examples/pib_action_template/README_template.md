pib action template

Für die ROS2-Funktionen im pib sollten einheitliche Strukturen verwendet werden, um das Code-Verständnis zu erleichtern. Dies ist ein Vorschlag für die Struktur von ROS2-Actions. 



ROS2 Actions allgemein

Actions eignen sich für Funktionen, die zu beliebigen Zeitpunkten gestartet werden können. Sie werden durch einen Action Server bereitgestellt und der Action Client eignet sich dazu, die Funktion im Server strukturiert aufzurufen. Der Server wird bereits beim Hochfahren des Systems gestartet und kann dann jederzeit aufgerufen werden.

Nähere Beschreibung zu ROS2 Actions: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html



Action Template Beschreibung

Im vorliegenden Action Template sind alle nötigen Funktionen für die allgemeine Funktion von Actions enthalten


Action Template Server

__init__(self): # action server construction
Erstellt den Server über den Konstruktor und verlinkt Callback-Funktionen
Verlinkt die Funktionen goal_callback und execute_callback für die Reaktion auf das Empfangen eines neuen Goals

goal_callback(self, goal_request): # received Goal from Action Client
Funktion, die prüft, ob das Goal die nötigen Elemente enthält und ob diese in den geforderten Grenzen liegen
Annehmen durch return GoalResponse.ACCEPT
Ablehnen durch return GoalResponse.REJECT
        
def execute_callback(self, goal_handle): # execution function
Funktion, die die Kernfunktionalität hinter der Action startet, nachdem das Goal akzeptiert wurde
import der eigenen Kernfunktion nicht vergessen
Erhält das Ergebnis aus der Kernfunktionalität, übernimmt error handling
Liefert das Ergebnis per Return an den Client zurück

main # entry point for Action Server
Programm wird an dieser Stelle gestartet

rclpy.spin() # run action client until rclpy.shutdown()
Server läuft nach dem Starten ununterbrochen weiter, um die Funktion dauerhaft bereitzustellen
Wird erst beim Herunterfahren des Systems oder durch den Befehl rclpy.shutdown() beendet
Programmablauf verbleibt in rclpy.spin(), der Code nach dieser Zeile wird nicht automatisch ausgeführt
rclpy.shutdown() muss also durch andere Abläufe (zB error handling, shutdown) ausgeführt werden.



Action Template Client

__init__(self): # action client construction
Erstellt den Server über den Konstruktor

def send_goal(self, goal_content): # send goal to server to initiate action execution
Generiert Goal-Datentyp nach Schnittstellenbeschreibung in action/Template.action und sendet Goal an den Server, sobald dieser verfügbar ist
Verlinkt Funktion goal_response_callback für Rückmeldung über goal-Akzeptanz
Verlinkt Funktion feedback_callback für die Rückmeldung von Feedback-Meldungen vom Server

def goal_response_callback(self, future): # response from action server, goal is accepted or rejected
Erhält die Meldung über Akzeptanz des Goals
Beendet den Clients nach Ablehnung des Goals
Wartet auf Result des Servers durch goal_handle.get_result_async() nach Akzeptanz des Goals
Verlinkt Funktion get_result_callback für Rückmeldung nach der Ausführung des Servers

def feedback_callback(self, feedback_msg): # feedback response function, get feedback from action server
Erhält Feedback-Meldungen vom Server
Gibt das Feedback weiter an übergeordnete Funktionen

def get_result_callback(self, future): # result response function, get result from action Server
Erhält Result vom Server nach der Ausführung
Gibt Result weiter an übergeordnete Funktionen
Beendet Action Client nach der Rückmeldung

main # entry point for Action Server
Programm wird an dieser Stelle gestartet
action_client.send_goal führt das senden des Goals an den Server aus

rclpy.spin() # run action client until rclpy.shutdown()
Client läuft nach dem Starten ununterbrochen weiter, um die Funktion dauerhaft bereitzustellen
Wird erst beim Herunterfahren des Systems oder durch den Befehl rclpy.shutdown() beendet
Programmablauf verbleint in rclpy.spin(), der Code nach dieser Zeile wird nicht automatisch ausgeführt
rclpy.shutdown() wird in den Client-Funktionen nach Ablehnung des Goals oder nach Beenden des Ablaufs ausgeführt



Hinzufügen weiterer Module zum Action-Paket

Werden weitere Module für die Funktion der Action gebraucht, müssen diese in Setup.py unter "entry_points" hinzugefügt werden
Die Struktur entspricht dabei 'executable_name = ordner.name_python_datei:funktionsname_entry_point',




Starten der Funktion

Zum Ausführen wird auf der Kommandozeile der ros2-Befehl ausgeführt:

ros2 run package_name executable_name

Anwendungsbeispiel:
Nach dem Hochfahren des Systems, Terminal 1:
ros2 run pib_action_template action_template_server
--> Server wird gestartet, wartet auf goal

Zum Ausführen der Funktion, Terminal 2:
ros2 run pib_action_template action_template_client
--> Client wird gestartet, sendet goal zum Server
--> Funktion läuft einmal durch



Anmerkungen zu ROS2-Services

Nähere Beschreibung zu ROS2-Services: https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Service-And-Client.html

Services in ROS2 bieten sich ebenfalls an, Funktionen bereitzustellen, die zu beliebigen Zeitpunkten aufgerufen werden können. Services in haben eine ähnliche Funktion wie Actions, jedoch keine Feedback-Meldungen. Daher eignen sich Services für Funktionen mit nur einem Ergebnis und der Aufbau unterscheidet sich daher von Actions. Elemente wie GoalResponse.ACCEPT und GoalResponse.REJECT existieren nicht in Services, daher muss die Aktzeptanz der Startinformationen anders gehandhabt werden als in Actions.

Actions können allerdings auch wie Services benutzt werden, indem einfach keine Feedback-Meldungen verwendet werden. Die zusätzlichen Elemente in Actions ermöglichen mehr Kontrolle über die Elemente und den Ablauf. Daher können alle Funktionen, die Services erfordern, auch mit Actions realisiert werden. Außerdem ist das Erstellen eines weiteren Templates für Services nicht nötig, was auch die Komplexität des Systems verringert.
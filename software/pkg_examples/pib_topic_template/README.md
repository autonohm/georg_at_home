pib topic template

Für die ROS2-Funktionen im pib sollten einheitliche Strukturen verwendet werden, um das Code-Verständnis zu erleichtern. Dies ist ein Vorschlag für die Struktur von ROS2-Topics. 



ROS2 Topics allgemein

Topics in ROS2 arbeiten nach dem Publisher-Subscriber-Prinzip. Topics eignen sich dazu, Information an mehrere Subscriber innerhalb eines Systems zu verteilen. Jeder Subscriber kann auf mehrere Topics unterschiedlicher Publisher hören und die Daten empfangen. Jedes Topic hat seinen eigenen einmaligen Namen.

Nähere Beschreibung zu ROS2-Topics: https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html



Topic Template Beschreibung

Im vorliegenden Topic Template sind alle nötigen Funktionen für die allgemeine Funktion von Publisher und Subscriber enthalten



Topic Template Subscriber

__init__(self): # topic subscriber construction
Erstellt den Subscriber über den Konstruktor
Definiert den Namen des Topics und den Datentyp des Dateninhalts
Verlinkt die Funktion subscriber_callback für die Reaktion auf den Empfang eines Publishs dieses Topics

subscriber_callback(self, msg): # publsih response function
Funktion, die auf den Publish eines Topics reagiert
Wird ausgeführt sobald neue Daten dieses Topics empfangen werden

main # entry point for topic subscriber
Programm wird an dieser Stelle gestartet

rclpy.spin() # run topic subscriber until rclpy.shutdown()
Subscriber läuft nach dem Starten ununterbrochen weiter, um die Topics dauerhaft zu empfangen
Wird erst beim Herunterfahren des Systems oder durch den Befehl rclpy.shutdown() beendet
Programmablauf verbleint in rclpy.spin(), der Code nach dieser Zeile wird nicht automatisch ausgeführt
rclpy.shutdown() muss also durch andere Abläufe (zB error handling, shutdown) ausgeführt werden.



Topic Template Timed Subscriber

__init__(self): # topic Publisher construction
Erstellt den Publisher über den Konstruktor
Definiert den Namen des Topics und den Datentyp des Dateninhalts
Definiert einen Timer mit vorgegebener Zeitspanne und verlinkt Funktion timer_callback, die nach Ablauf der Zeitspanne immer wieder ausgeführt wird

def timer_callback(self): # publishing function, starting after time pause
Generiert Topic-Daten und publisht diese direkt im Anschluss

main # entry point for topic publisher
Programm wird an dieser Stelle gestartet

rclpy.spin() # run topic Publisher until rclpy.shutdown()
Publisher läuft nach dem Starten ununterbrochen weiter, um die Topics dauerhaft zu publishen
Wird erst beim Herunterfahren des Systems oder durch den Befehl rclpy.shutdown() beendet
Programmablauf verbleint in rclpy.spin(), der Code nach dieser Zeile wird nicht automatisch ausgeführt
rclpy.shutdown() muss also durch andere Abläufe (zB error handling, shutdown) ausgeführt werden.



Topic Template Triggered Publisher

__init__(self): # topic Publisher construction
Erstellt den Publisher über den Konstruktor
Definiert den Namen des Topics und den Datentyp des Dateninhalts

def trigger_callback(self): # publishing function
Generiert Topic-Daten und publisht diese direkt im Anschluss

main # entry point for topic publisher
Programm wird an dieser Stelle gestartet

topic_template_publisher.trigger_callback() initiiert das Publishen des Topics genau einmal
topic_template_publisher.destroy_node() # shutdown the node explicitly und rclpy.shutdown() beenden den Publisher nach einmaligen Publishen automatisch



Hinzufügen weiterer Module zum Topic-Paket

Werden weitere Module für die Funktion des Topics gebraucht, müssen diese in Setup.py unter "entry_points" hinzugefügt werden
Die Struktur entspricht dabei 'executable_name = ordner.name_python_datei:funktionsname_entry_point',



Starten der Funktion

Zum Ausführen wird auf der Kommandozeile der ros2-Befehl ausgeführt:

ros2 run package_name executable_name

Anwendungsbeispiel:
Nach dem Hochfahren des Systems, Terminal 1:
ros2 run pib_topic_template subscriber
--> Subscriber startet, wartet auf Daten

Zum Ausführen der Funktion, Terminal 2:
ros2 run pib_topic_template topic_template_triggered_publisher
--> Publisher wird gestartet
--> Topic wird einmal gepublisht
--> Publisher wird wieder beendet

ros2 run pib_topic_template topic_template_timed_publisher
--> Publisher wird gestartet
--> Topic wird dauerhaft gepublisht
--> Publisher läuft bis zum manuellen Beenden weiter
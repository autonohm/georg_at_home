## pib demo template

Dieses Demo vereint die Funktionen von Actions und Topics. Es werden ein Action Server und ein Action Client nach dem Template-Schema bereitgestellt. Diese beiden nutzen zusätzlich noch das Publisher-Subscriber Prinzip, um nach einem Druchlauf automatisch einen weiteren Durchlauf zu starten.


### Beschreibung der Demo-Funktion

Die Demo Funktion veranschauchlicht ein mögliches Zusammenspiel zwischen Actions und Topics durch eine Interaktion zwischen Server und Client.


#### Demo Server

Der Demo Server wird gestartet und stellt die generelle Action Server Funktion bereit. Zusätlich erstellt der Server einen Publisher, der auf ein Neustart-Topic eine leere Neustart-Nachricht publisht. Es ist kein Inhalt in der Nachricht nötig, da nur das publishen der Nachricht selbst relevant ist. Nach einem Durchlauf des Servers wird diese Nachricht gepublisht, um einen neuen Durchlauf zu generieren.


#### Demo Client

Der Demo Client wird nach dem Server gestartet. Der Client erstellt zusätzlich einen Subscriber auf das Neustart-Topic, der vom Server die leere Neustart-Nachricht erhält. Nach dem Erhalt dieser Nachricht wird automatisch ein neues Goal gesendet.


### Ablauf

1. Server starten
* Action Server Funktion wird bereitgestellt
* Publisher auf Neustart-Topic wird erstellt
-> Server bereit

2. Client starten
* Action Client Funktion wird bereitgestellt
* Subscriber auf Neustart-Topic wird ertstellt

3. Endlosschleife läuft ab
-> Client sendet nach Start Initial-Goal automatisch
-> Server erhält Goal, arbeitet Action ab
-> Server generiert Result
-> Server publisht leere Neustart-Nachricht und sendet Result an Client
-> Client erhält Neustart-Nachricht und Result
-> Client sendet neues Goal an Server
-> Neuer Durchlauf startet
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

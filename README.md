# EWS
Dieses Repo enthällt alle Ergebnisse des Projektseminars Eyes Wide Scroll an der Universität Münster. 
Im Laufe dieses Seminares haben wir eine Studie durchgeführt, in der wir mit einem Tobii Pro Spark Eye-Tracking Daten von Probanden gesammelt haben. Gezeigt wurden Bilder mit Verschiedenen Eigenschaften, die die Nutzer für 5 bis 15 Sekunden betrachten sollten. 

## code
Dieser Ordner enthällt jeglichen geschriebenen Code

### analysis
Auf basis der Daten, die wir im Rahmen der Studie gesammelt haben, haben wir verschiedene Analysen durchgeführt. Diese sind jeweils in einem Eigenen Ordner weiter ausgeführt. Die Ordner enthallten sowohl jeglichen Code, als auch weitere zur Analyse notwenidge Daten.

### dehydration
Um Urherberrecht zu wahren wurden die Bilder, die nicht aus Creative Commons stammten "dehydriert". Mittels crop_data.json können sie rekonstruiert werden, wenn das Dataset geteilt werden soll.

### experiment
enthällt Code für das Pilottesting, dass wir im Vorhinein zur eigentlichen Studie durchgeführt haben.
Zum weiterführenden Verständnis des Technischen Setups kann die entsprechende Readme gelsesen werden: [Technisches Setup](code/experiment/README.md)

### preprocess
Bevor die Dateien zur Analyse verwendet werden konnten, wurden diese preprocessed. Das inkludiert zum Beispiel das Berechnen von Fixationen, aber auch erste Visualisierungen, in der Form von Heatmaps oder Scanpaths.


## data
Dieser Ordner enthällt die allgemeinen Dateien, die in der Studie zum einsatz gekommen sind. 

### img
Die in der Studie verwendeten Bilder

### raw
Die Rohdateien, der in der Studie gesammelten Daten.
Pro Proband und pro Bild ist jeweils eine .csv datei vorhanden, die die allgemein vom Eye-Tracker gesammelten Daten, sowie Time-Stamps und eine Validität enthällt.

### validation
Jeder Proband sollte am Ende der Studie für 10 Bilder beantworten, ob diese in den vorherigen Bildern bereits aufgetaucht sind. Dadurch wollten wir sicher gehen, dass alle Probanden die Bilder auch eingehend betrachten und nicht nur schnellstmöglich durchklicken. Pro proband ist in diesem Ordner eine Ergebnisdatei gespeichert, die diesen Text enthällt

## doc
Zu den analysen haben wir eine Arbeit geschrieben, die die Analyseergebnise knapp erläutert. Diese kann unter doc/Latex Abschlussarbeit/main.pdf  gelesen werden.

Unter doc/Durchführung der Studie findet sich eine Zusammenfassung von Studiendesign und -ablauf sowie technischem Setup.
# EWS
Dieses Repo enthält alle Ergebnisse des Projektseminars Eyes Wide Scroll an der Universität Münster. 
Im Laufe dieses Seminares haben wir eine Studie durchgeführt, in der wir mit einem Tobii Pro Spark Eye-Tracking Daten von Probanden gesammelt haben. Gezeigt wurden Bilder mit verschiedenen Eigenschaften, die die Nutzer für 5 bis 15 Sekunden betrachten sollten. 

## code
Dieser Ordner enthält jeglichen geschriebenen Code.

### analysis
Auf Basis der Daten, die wir im Rahmen der Studie gesammelt haben, haben wir verschiedene Analysen durchgeführt. Diese sind jeweils in einem eigenen Ordner weiter ausgeführt. Die Ordner enthalten sowohl jeglichen Code, als auch weitere zur Analyse notwendige Daten.

### dehydration
Um Urherberrecht zu wahren wurden die Bilder, die nicht aus Creative Commons stammten, "dehydriert". Mittels crop_data.json können sie rekonstruiert werden, wenn das Dataset geteilt werden soll.

### experiment
Enthält Code für das Pilottesting, das wir im Vorhinein zur eigentlichen Studie durchgeführt haben.
Zum weiterführenden Verständnis des Technischen Setups kann die entsprechende Readme gelesen werden: [Technisches Setup](code/experiment/README.md)

### preprocess
Bevor die Dateien zur Analyse verwendet werden konnten, wurden diese vorverarbeitet. Das inkludiert zum Beispiel das Berechnen von Fixationen, aber auch erste Visualisierungen, in der Form von Heatmaps oder Scanpaths.

## data
Dieser Ordner enthält die allgemeinen Dateien, die in der Studie zum Einsatz gekommen sind. 

### img
Die in der Studie verwendeten Bilder

### raw
Die Rohdateien der in der Studie gesammelten Daten.
Pro Proband und pro Bild ist jeweils eine .csv datei vorhanden, die die allgemein vom Eye-Tracker gesammelten Daten sowie Time-Stamps und eine Validität enthält.

### validation
Jeder Proband sollte am Ende der Studie für 10 Bilder beantworten, ob diese in den vorherigen Bildern bereits aufgetaucht sind. Dadurch wollten wir sicher gehen, dass alle Probanden die Bilder auch eingehend betrachten und nicht nur schnellstmöglich durchklicken. Pro Proband ist in diesem Ordner eine Ergebnisdatei gespeichert, die diesen Text enthält.

## doc
Zu den Analysen haben wir eine Arbeit geschrieben, die die Analyseergebnise knapp erläutert. Diese kann unter doc/Latex Abschlussarbeit/main.pdf gelesen werden.

Unter doc/Durchführung der Studie findet sich eine Zusammenfassung von Studiendesign und -ablauf sowie technischem Setup.

# Technical Setup

# Aufbau
* Theorie
* Setup
    * Hardware Setup
    * Software Setup
* Libaries
* Pilottesting-Skript Anleitung
* Grundlagen für eigene Experimente

# Theorie

## Eyetracker
Ein Eyetracker ist ein technisches Gerät, das die Bewegungen und Blickrichtungen der Augen präzise erfasst. Dazu werden meist Infrarotlicht und spezielle Kameras eingesetzt. Zunächst sendet ein Infrarot-Emitter unsichtbare Lichtstrahlen aus, die auf die Hornhaut treffen und reflektiert werden. Die reflektierten Lichtpunkte werden von einer hochauflösenden Kamera aufgenommen. Mithilfe von Algorithmen wird der Abstand zwischen dem reflektierten Licht und dem Zentrum der Pupille berechnet, sodass das System genau bestimmen kann, wohin der Nutzer blickt. Diese Information wird in Echtzeit in Form eines „Gaze Points“ auf dem Bildschirm oder in einer virtuellen Umgebung dargestellt. Vor jeder Messung ist eine Kalibrierung erforderlich, bei der der Nutzer mehrere Punkte fixiert, damit das System die individuellen Augenbewegungen korrekt interpretieren kann. 

### Mobile Eyetracker
Mobile Eyetracker sind tragbare Geräte, meist in Form von Brillen oder Headsets, die Augenbewegungen in Echtzeit erfassen. Mithilfe von Kameras und Algorithmen analysieren sie den Blickverlauf in natürlichen Umgebungen. Ihr Vorteil liegt in der Bewegungsfreiheit und der präzisen Erfassung von Fixationen und Blickverläufen, was wertvolle Einblicke in Wahrnehmung und Entscheidungsprozesse ermöglicht.

### Externe Eyetracker
Externe Eyetracker sind stationäre Systeme, die mithilfe von Infrarotkameras und Bildverarbeitung die Augenbewegungen einer Person erfassen, ohne dass diese ein Gerät tragen muss. Sie werden vor allem für Bildschirmanalysen, kognitive Forschung und Werbewirkungsstudien genutzt. Da sie eine hohe Präzision bieten und in kontrollierten Umgebungen arbeiten, eignen sie sich besonders für detaillierte Experimente und Usability-Tests. Diese Art von Eyetracker steht auch im Lab.

[Source](https://www.tobii.com/resource-center/learn-articles/how-do-eye-trackers-work)

## Gaze
Der Gaze ist die Blickrichtung von dem Auge, was von einem Eyetracker beobachtet wird. Der Punkt an dem diese Blickrichtung mit etwas kollidiert wird Gaze Point genannt. Dieser Punkt ist ein Punkt im 3 Dimensionalem Bereich, kann aber für externe Eyetracker normalisiert werden, um dem 2D Koordinatensystem des Bildschirms zu entsprechen.

## Augenbewegungen
Es wird in mehrere Augenbewegungen unterschieden, die uns helfen die Bilderfassung zu analysieren.

* Blickpunkte (Gaze Points)
    * Kleinste Messeinheit der Augenbewegung
    * Jeder Datenpunkt entspricht einem erfassten Blick
* Fixationen
    * Gruppe räumlich und zeitlich nahe beieinander liegender Blickpunkte
    * Augen verweilen auf einem Objekt (100–300 ms)

* Folgebewegung
    * Verfolgen eines sich bewegenden Objekts

* Sakkaden
    * Schnelle Augenbewegungen zwischen Fixationen
    * Typisch beim Lesen: Sprunghafte Bewegung über Textzeilen

* Blickpfade
    * Abfolge von Fixation → Sakkade → Fixation
    * Zeigt die visuelle Erkundung eines Stimulus

## wichtigste Biases

* Accuracy Bias
    * Der Eye Tracker berechnet einen Blickpunkt, der leicht vom tatsächlichen Fixationspunkt abweichen kann

* Head Movement Bias
    * Ungenauigkeit bei Bewegung des Kopfes während der Messung

* Lighting Bias
    * Fehlmessungen durch stark wechselnde Lichtverhältnisse

* Drift
    * Tracker weicht von ursprünglicher Kalibrierung ab z. B. bei langen Sessions oder instabiler Hardware

* Screen Position Bias
    * Messungen sind am Rand des Bildschirms oft ungenauer als in der Mitte



# Setup
## Hardware Setup
* Um den Eyetracker zu benutzen wird ein Computer, Bildschirm und ein Tobii Pro Eye Tracker benötigt.

* Der Eyetracker wird an dem unterem Rand vom Bildschirm festgeklebt

* Eyetracker und Bildschirm müssen per Kabel mit dem Computer verbunden werden

## Software Setup
* Herunterladen des [Tobii Pro Eye Tracker Manager](https://www.tobii.com/products/software/applications-and-developer-kits/tobii-pro-eye-tracker-manager#downloads)

* Herunterladen des Treibers für 'Tobii Pro Spark' innerhalb des Managers

* Eye-Tracker anschließen und mit dem Manager kalibrieren (einmalig am Anfang zur Monitorkalibrierung; Kalibrierung sollte sonst für jeden Nutzer erneut durchgeführt werden)

* Installation der tobii_research Python-Library mit 'pip install tobii_research'

* Python Version 3.10 oder 3.11.3 muss verwendet werden (evtl. auch andere, diese haben wir aber nicht getestet)

* Beliebiger Code Editor (bespielsweise Visual Studio Code)

# Libaries

## Tobii SDK
Einen Link zur offizellen Dokumentation findet ihr [hier](https://developer.tobiipro.com/python.html).
Die folgenden Python Funktionen sind nicht teil der tobii_research Library und müssen manuell implementiert werden.

* Zu Beginn eines Projekts die Library und beliebige Hilfslibraries importieren. Hier die von uns fürs Hauptskript verwendeten Libraries: 
 
        import tobii_research as tr
        import time
        import os
        import csv
        import pygame

* Mit Eye-Tracker verbinden:
        
        def find_tracker():
    
            found_eyetrackers = tr.find_all_eyetrackers()

            if (len(found_eyetrackers) > 0):
                pTracker = found_eyetrackers[0]
                print("Eye-Tracker connected: " + pTracker.device_name)
                return pTracker
            else:
                print("No Eye-Trackers found!")

* Eye-Tracker per Code kalibrieren:

        def calibrate_tracker(pTracker):
            screen_width, screen_height = screen.get_size()
            print("Trying Calibration")
            calibration = tr.ScreenBasedCalibration(pTracker)
            calibration.enter_calibration_mode()

            points_to_calibrate = [(0.5, 0.5), (0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9)]
            for point in points_to_calibrate:
                x = int(point[0] * screen_width)
                y = int(point[1] * screen_height)
                r = 10

                screen.fill((0, 0, 0))
                pygame.draw.circle(screen, 'red', (x - r, y - r), r)
                pygame.display.flip()

                time.sleep(3)

                if calibration.collect_data(point[0], point[1]) != tr.CALIBRATION_STATUS_SUCCESS:
                    calibration.collect_data(point[0], point[1])

            calibration_result = calibration.compute_and_apply()

            calibration.leave_calibration_mode()
    Bevor diese Methode aufgerufen werden kann, muss ein pygame folgendermaßen initialisiert werden:
    
        pygame.init()
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
* Aufnahme starten und aufgenommene Daten erhalten:


        def gaze_data_callback(gaze_data):
            ...
        
        tracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback,as_dictionary=True)
    Die Funktion 'gaze_data_callback' wird mehrmals in der Sekunde aufgerufen und definiert, was mit den aufgenommenen Daten geschieht. Das Dictionary 'gaze_data' beinhaltet die Daten der Aufnahme in dem Moment. Beispiel für gaze_data_callback:
    
        list = []
        def gaze_data_callback(gaze_data):
            list.append(gaze_data)

* Der Inhalt von 'gaze_data':
    'gaze_data' ist ein Dictionary mit folgenden Keys:
    * device_time_stamp: 
        *Zeitsptempel des Eye-Trackers in Mikrosekunden*
        
    * system_time_stamp:
        *Zeitstempel des Systems in Mikrosekunden*
    
    Die folgenden Daten sind je für das **rechte** und **linke Auge** verfügbar. Hierzu muss lediglich '**left**' mit '**right**' ersetzt werden:
    * left_gaze_point_on_display_area:
       * *(x, y) Koordinaten der Blickposition auf dem Display (normalisiert von 0 bis 1).*
       * *(0, 0) stellt die linke, obere Ecke des Bildschirms dar, (0.5, 0.5) die Mitte und (1, 1) die rechte, untere Ecke.*
       * *Zum umrechnen muss der normalisierte Wert mit der Pixelanzahl des Monitors multipliziert werden*
        
    * left_gaze_point_in_user_coordinate_system:
        * *(x, y, z) Position des Blickpunkts (was schaut der Nutzer an) im Benutzersystem*
        * *Das Benutzersystem ermittelt die Position der Augen relativ zum Benutzer. Bezugspunkt ist ein Referenzpunkt im Gesicht.*
        * *Angaben in mm*
         
    * left_gaze_point_validity:
        * *Gibt an, ob die Daten für das linke Auge gültig sind (0 = ungültig, 1 = gültig)*
        * *Kann z.B. auf blinzeln oder Aufnahmefehler hinweisen*
        
    * left_pupil_diameter:
        * *Pupillendurchmesser (in mm)*
        
    * left_pupil_validity:
        * *Gibt an, ob die Daten für die linke Pupille gülitg sind(0 = ungültig, 1 = gültig)*
        * *Kann z.B. auf blinzeln oder Aufnahmefehler hinweisen*
        
    * left_gaze_origin_in_user_coordinate_system:
        * *(x, y, z) Position des Blickpstrahlursprungs im Benutzersystem*
        * *Das Benutzersystem ermittelt die Position der Augen relativ zum Benutzer. Bezugspunkt ist ein Referenzpunkt im Gesicht.*
        * *Angaben in mm*
        
    * left_gaze_origin_validity:
        * *Gibt an, ob eine gültige Position für den Ursprung des Blickstrahls eines Auges bestimmt werden konnte (0 = ungültig, 1 = gültig)*

* Aufnahme stoppen:
            
        tracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    Da die Aufnahme eine gewisse Zeit dauern soll, ist zu empfehlen mit 'time.sleep()' zwischen Start und Stopp zu arbeiten
* Aufgenommenes in csv-Datei abspeichern

        with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
            # Bestimme die Feldnamen basierend auf den Keys des ersten Dictionaries
            feldnamen = list[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=feldnamen)

            # Schreibe die Kopfzeile
            writer.writeheader()

            # Schreibe die Datenzeilen
            writer.writerows(list)
   
   
## Alternative Python Packages

Weitere Packages, welche benutzt werden können, wir aber nicht weiter im Detail betrachtet haben.

- **PsychoPy**
    - https://www.psychopy.org/
- **PyGaze**
    - http://www.pygaze.org/
    - https://osdoc.cogsci.nl/manual/eyetracking/pygaze/
- **OpenSesame**
    - https://osdoc.cogsci.nl/


# Pilottesting-Skript Anleitung
## Anleitung

### Wichtiges vorm Ausführen
(Beachte Hardware und Software Setup)
Für das folgende Skript, muss ein txt-Dokument im selben Arbeitsverzeichnis mit dem Namen "ProbandID.txt" angelegt werden, in welchem die momentane Nummer des Probanden steht (initial also idealerweise 0 bzw. 1). Dieses Dokument stellt das kontinuierliche Inkrementieren der IDs sicher, auch über mehrere Sessions hinweg. Außerdem sollte das Programm mit "Escape" möglichst nur beendet werden, sobald ein neuer Proband kalibriert werden soll, sprich nach einem vollständigen Durchlauf eines Probanden, da sonst unvollständige Ergebnisse aufkommen (dies ist aber manuell zu beheben: einfach das txt-Dokument manuell um 1 verringern und die unvollständigen Testergebnisse löschen). Außerdem sind zwei Ordner mit Bildern nötig, deren Dateipfade den Variablen "folder_path" und "control_path" übergeben werden müssen. Die Bilder von "folder_path" sind die zur Studie verwendeten Bilder und die von "control_path" sind am Ende verwendete, nicht in der Studie verwendete Bilder, um zu testen ob der Proband auch aufmerksam zugeschaut hat. Somit sollte kein Bild in sowohl "control_path" als auch in "folder_path" auftauchen.

### Was macht das Skript?
Beim Starten des Skripts wird sich zunächst mit dem Eye-Tracker verbunden. Danach durchläuft das Skript bis zum Beenden durch Escape eine Reihe von Schritten:
Zunächst startet ein Kalibrierungsprogramm, bei dem der Proband der Reihe nach auf erscheinende rote Punkte schauen muss, bis diese verschwinden. 
Danach werden in zufälliger Reihenfolge die Bilder des unter "folder_path" angegebenen Ordners nacheinander angezeigt. Die oben im Skript angegebenen Zeiten "max_time" und "min_time" geben hier jeweils an, wie lange die Bilder mindestens und maximal in Sekunden angezeigt werden. Ab der minimal-Zeit hat der Proband die Möglichkeit, mit der Leertaste oder rechten Pfeiltaste das nächste Bild anzeigen zu lassen. Bei erreichen der maximal-Zeit wird automatisch das nächste Bild angezeigt. Nach jedem Bild wird eine csv-Datei erstellt, welche die ProbandenID, die BildID und einen Time-Stamp im Namen beinhaltet erstellt, welche die gaze-data enthält. 
Sobald alle Bilder durchlaufen wurden, muss der Proband eine Validitätskontrolle durchlaufen. Diese startet er mit 'S'. Es werden nun in zufälliger Reihenfolge eine gleichmäßig verteilte Mischung von Bildern aus "folder_path" und "conrol_path" angezeigt (genau so viele Bilder aus "folder_path" wie in "control_path" vorhanden sind) und der Proband muss mit 'J' für "Ja" und mit 'N' für "Nein" stimmen, ob er die Bilder bereits gesehen hat. Daraus wird dann eine csv-Datei erstellt, welche "Valididätskontrolle" im Namen hat. 
Danach wird gefragt ob der nächste Proband kalibriert werden soll. Dies kann mit der Leertaste oder der rechten Pfeiltaste bestätigt werden und das Programm startet von vorne, also erneut mit der Kalibrierung.

## Pilottesting-Skript

    import tobii_research as tr
    import pygame
    import random
    import os
    import csv
    import time


    with open('ProbandID.txt', 'r', encoding='utf-8') as f:
        proband = f.read().strip()
        proband = int(proband)

    list = []
    folder_path = 'current_images/'
    control_path = 'control_images/'
    max_time = 15 # Max Anzeigedauer in s
    min_time = 5  # Min Anzeigedauer in s



    def gaze_data_callback(gaze_data):
        #if(index < len(images)):
        #    gaze_data["Image"] = images[index]
        #else: gaze_data["Image"] = None
        list.append(gaze_data)


    def find_tracker():

        found_eyetrackers = tr.find_all_eyetrackers()

        if (len(found_eyetrackers) > 0):
            pTracker = found_eyetrackers[0]
            print("Eye-Tracker connected: " + pTracker.device_name)
            return pTracker
        else:
            print("No Eye-Trackers found!")
            return None


    def calibrate_tracker(pTracker):
        screen_width, screen_height = screen.get_size()

        calibration = tr.ScreenBasedCalibration(pTracker)
        calibration.enter_calibration_mode()

        points_to_calibrate = [(0.5, 0.5), (0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9)]
        for point in points_to_calibrate:
            x = int(point[0] * screen_width)
            y = int(point[1] * screen_height)
            r = 10

            screen.fill((0, 0, 0))
            pygame.draw.circle(screen, 'red', (x - r, y - r), r)
            pygame.display.flip()

            time.sleep(3)

            if calibration.collect_data(point[0], point[1]) != tr.CALIBRATION_STATUS_SUCCESS:
                calibration.collect_data(point[0], point[1])

        calibration_result = calibration.compute_and_apply()

        calibration.leave_calibration_mode()


    def scale_image(pImage):
        width, height = pImage.get_size()
        swidth, sheight = screen.get_size()

        if swidth - width < sheight - height:
            pImage = pygame.transform.smoothscale(pImage, (swidth, int((swidth / width) * height)))
        else:
            pImage = pygame.transform.smoothscale(pImage, (int((sheight / height) * width), sheight))

        return pImage


    def next_image():
        global index, images, image, list, proband, skip

        index += 1

        if index < len(images):
            if index == round(len(images) / 2):
                curtime = time.asctime().split(' ')[3].split(':')[0] + '_' + time.asctime().split(' ')[3].split(':')[1] + '_' + time.asctime().split(' ')[3].split(':')[2]

                with open('Proband' + str(proband) + '_' + curtime + '_' + images[index - 1].split(".")[0] + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
                    # Bestimme die Feldnamen basierend auf den Keys des ersten Dictionaries
                    feldnamen = list[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=feldnamen)
                    # Schreibe die Kopfzeile
                    writer.writeheader()
                    # Schreibe die Datenzeilen
                    writer.writerows(list)
                pause()
            else:
                image = pygame.image.load(r'' + folder_path + images[index])
                image = scale_image(image)

                curtime = time.asctime().split(' ')[3].split(':')[0] + '_' + time.asctime().split(' ')[3].split(':')[1] + '_' + time.asctime().split(' ')[3].split(':')[2]

                with open('Proband' + str(proband) + '_' + curtime + '_' + images[index - 1].split(".")[0] + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
                    # Bestimme die Feldnamen basierend auf den Keys des ersten Dictionaries
                    feldnamen = list[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=feldnamen)
                    # Schreibe die Kopfzeile
                    writer.writeheader()
                    # Schreibe die Datenzeilen
                    writer.writerows(list)

                list = []
                pygame.time.set_timer(skippable, min_time * 1000)
                pygame.time.set_timer(force_skip, max_time * 1000)

        elif index == len(images):
            curtime = time.asctime().split(' ')[3].split(':')[0] + '_' + time.asctime().split(' ')[3].split(':')[1] + '_' + time.asctime().split(' ')[3].split(':')[2]

            with open('Proband' + str(proband) + '_' + curtime + '_' + images[index - 1].split(".")[0] + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
                # Bestimme die Feldnamen basierend auf den Keys des ersten Dictionaries
                feldnamen = list[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=feldnamen)
                # Schreibe die Kopfzeile
                writer.writeheader()
                # Schreibe die Datenzeilen
                writer.writerows(list)

            control()

            image = pygame.font.Font(None, 74).render("Neuen Probanden kalibrieren? Dann jetzt '->' drücken", True, (255, 255, 255))

            pygame.time.set_timer(skippable, min_time*1000)
            pygame.time.set_timer(force_skip, 0)

        else:
            calibrate_tracker(tracker)
            index = 0
            random.shuffle(images)
            image = pygame.image.load(r'' + folder_path + images[index])
            image = scale_image(image)
            list = []
            proband += 1
            pygame.time.set_timer(skippable, min_time * 1000)
            pygame.time.set_timer(force_skip, max_time * 1000)

        skip = False


    def pause():
        global image, paused, tracker

        tracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

        pygame.time.set_timer(skippable, 0)
        pygame.time.set_timer(force_skip, 0)

        paused = True
        image = pygame.font.Font(None, 74).render("Pausiert. Drücke 'R' zum fortfahren", True, (255, 255, 255))


    def resume():
        global image, paused, list, folder_path, images, index, tracker

        tracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback,as_dictionary=True)

        calibrate_tracker(tracker)

        image = pygame.image.load(r'' + folder_path + images[index])
        image = scale_image(image)

        pygame.time.set_timer(skippable, min_time * 1000)
        pygame.time.set_timer(force_skip, max_time * 1000)

        list = []
        paused = False


    def control():
        global control_img, images, proband

        tracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

        if (len(control_img) <= len(images)):
            real = random.sample(range(len(images)), k=len(control_img))
            test = control_img.copy()
            for ind in real:
                test.append(images[ind])
            random.shuffle(test)

            first = pygame.font.Font(None, 74).render("Wurden die nachfolgenden Bilder in der Studie bereits gezeigt?", True, (255, 255, 255))
            second = pygame.font.Font(None, 74).render("'J' für Ja, 'N' für Nein, 'S' zum Starten", True, (255, 255, 255))

            screen.fill((0, 0, 0))
            screen.blit(first, (screen.get_width() / 2 - first.get_width() / 2, screen.get_height() / 2 - first.get_height() / 2 - 50))
            screen.blit(second, (screen.get_width() / 2 - second.get_width() / 2, screen.get_height() / 2 - second.get_height() / 2 + 50))
            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_s:
                            waiting = False

                pygame.display.update()

            correctness = []
            tmp = 0
            if test[tmp] in images:
                img = pygame.image.load(r'' + folder_path + test[tmp])
            else:
                img = pygame.image.load(r'' + control_path + test[tmp])
            img = scale_image(img)
            while tmp < len(test):
                screen.fill((0, 0, 0))
                screen.blit(img, (screen.get_width() / 2 - img.get_width() / 2, screen.get_height() / 2 - img.get_height() / 2))

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_j:
                            if test[tmp] in images:
                                correctness.append({'Bild':test[tmp], 'Erwartet':True, 'Angegeben':True})
                            else:
                                correctness.append({'Bild':test[tmp], 'Erwartet':False, 'Angegeben':True})

                            tmp = tmp + 1
                            if tmp < len(test):
                                if test[tmp] in images:
                                    img = pygame.image.load(r'' + folder_path + test[tmp])
                                else:
                                    img = pygame.image.load(r'' + control_path + test[tmp])
                                img = scale_image(img)

                        if event.key == pygame.K_n:
                            if test[tmp] in images:
                                correctness.append({'Bild':test[tmp], 'Erwartet':True, 'Angegeben':False})
                            else:
                                correctness.append({'Bild':test[tmp], 'Erwartet':False, 'Angegeben':False})

                            tmp = tmp + 1
                            if tmp < len(test):
                                if test[tmp] in images:
                                    img = pygame.image.load(r'' + folder_path + test[tmp])
                                else:
                                    img = pygame.image.load(r'' + control_path + test[tmp])
                                img = scale_image(img)

                pygame.display.update()

            curtime = time.asctime().split(' ')[3].split(':')[0] + '_' + time.asctime().split(' ')[3].split(':')[1] + '_' + time.asctime().split(' ')[3].split(':')[2]

            with open('Proband' + str(proband) + '_' + curtime + '_Valididitätskontrolle.csv', 'w', newline='', encoding='utf-8') as csvfile:
                    # Bestimme die Feldnamen basierend auf den Keys des ersten Dictionaries
                    feldnamen = correctness[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=feldnamen)

                    # Schreibe die Kopfzeile
                    writer.writeheader()

                    # Schreibe die Datenzeilen
                    writer.writerows(correctness)

        tracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback,as_dictionary=True)


    images = [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith('.png') or f.lower().endswith("jpeg") or f.lower().endswith("jpg")]
    if not images:
        print("Keine Bilder im Ordner gefunden.")

    control_img = [f for f in sorted(os.listdir(control_path)) if f.lower().endswith('.png') or f.lower().endswith("jpeg") or f.lower().endswith("jpg")]
    if not control_img:
        print("Keine Bilder im Krontrollordner")

    random.shuffle(images)
    index = 0


    pygame.init()
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    tracker = None
    tracker = find_tracker()
    calibrate_tracker(tracker)


    force_skip = pygame.USEREVENT
    skippable = pygame.USEREVENT + 1


    image = pygame.image.load(r'' + folder_path + images[index])
    image = scale_image(image)

    tracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback,as_dictionary=True)
    skip = False
    paused = False
    run = True
    pygame.time.set_timer(skippable, min_time * 1000)
    pygame.time.set_timer(force_skip, max_time * 1000)
    while run:
        screen.fill((0, 0, 0))
        screen.blit(image, (screen.get_width() / 2 - image.get_width() / 2, screen.get_height() / 2 - image.get_height() / 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

                if (event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE) and skip and not paused:
                    next_image()

                if event.key == pygame.K_p and not paused:
                    pause()

                if event.key == pygame.K_r and paused:
                    resume()

            elif event.type == force_skip:
                next_image()

            elif event.type == skippable:
                skip = True
                pygame.time.set_timer(skippable, 0)


        pygame.display.update()

    tracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    pygame.quit()


    with open ('ProbandID.txt', 'w', encoding='utf-8') as f:
        f.write(str(proband + 1))



# Grundlagen für eigene Experimente
Die Durchführung des Experiments kann auf verschiedene Art erfolgen. Zum einen können nacheinander Bilder gezeigt werden. Zum anderen kann ein realitätsnäheres Format gewählt werden, bei dem der Nutzer mit dem Gezeigten interagieren kann, indem zum Beispiel gescrollt wird. Dazu muss der Bildschirm zeitgleich zum Eye-Tracker aufgenommen werden.

## Datensicherung

Die gesammelten Daten können in einer CSV-Datei abgespeichert werden. Diese enthält dann die Informationen, welche das Dicitonary 'gaze_data' beinhaltet.

Diese Daten können dann auf verschiedene Weise visualisiert werden, z.B. durch eine Heatmap oder eine Rekonstruktion der Bewegungen des Gazepoints.

Alternativ ist eine Livevisualisierung des Gazepoints möglich, um live zu beobachten, wo der Nutzer hinschaut.

## Bild

Zur Durchführung muss der Eye-Tracker zeitgleich mit dem ersten Bild gestartet werden. Sollten die Bilder wechseln, müssen die Zeitpunkte gespeichert werden.

### Visualisierung

Die Ergebnisse können mit OpenCV-Python visualisiert werden. Jeder einzelne Frame wird nacheinander hinzugefügt und kann entsprechend bearbeitet werden. Der Blickpunkt kann aus der Ausgabe des Eye-Trackers übernommen werden und als Punkt zum Frame hinzugefügt werden.

Hier werden der Einfachheit halber nur die Punkte eines Auges verarbeitet. Für ein exakteres Ergebnis müssen auch andere gemessene Daten in den Blickpunkt einfließen.

Für die Initialisierung des VideoWriters werden unter anderem ein Video-Codec und die FPS benötigt.

+ Der Video-Codec kann beliebig gewählt werden, muss allerdings das Dateiformat, der Ausgabedatei unterstützen. "mp4v" unterstützt zum Beispiel mp4-Dateien.

+ Die FPS-Zahl entspricht der Geschwindigkeit, mit der OpenCV die eingefügten Bilder abspielt. Für eine korrekte Darstellung muss die Zahl gleich der Menge der vorhandenen Daten/Sekunde sein.
Der Tobii Eye-Tracker macht in der Regel 60 Aufnahmen/Sekunde.

        import cv2
        
        fps = 60 
        # mp4v-Codec ist optimiert für mp4-Dateien
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_video = cv2.VideoWriter(Filepath, fourcc, fps, (width, height))
        
        
+  x, y sind die Koordinaten, die zuvor aus dem CSV-Dokument entnommen wurden.
eye_data ist eine Liste, die Tupel von allen Koordinaten der Gazes enthält.
eye_data enthält die vom Eye-Tracker ausgegebenen Daten. x, y sind die Koordinaten eines Blickpunktes

        for (x, y) in eye_data:
            frame = background.copy()

            # Bedingung nur abhängig von der Implementierung nötig. 
            # So wird für NaN-Einträge kein Punkt angezeigt
            if not (math.isnan(x) and math.isnan(y)):
                cv2.circle(frame, (x, y), 10, (0, 0, 255), -1)
            output_video.write(frame)

        output_video.release()

## Interaktion
Eine weitere Möglichkeit ist das Erlauben von Interaktionen mit dem Gezeigten. Hier kann zum Beispiel der Nutzer durch Social-Media-Websites scrollen. Dazu muss der Bildschirm aufgenommen werden, um später die Blickpunkte den Objekten zuordnen zu können.

### Aufnahme

Die Aufnahme des Videos kann zum Beispiel mithilfe von mss erfolgen. Mss ist eine Python-Bibliothek, die es erlaubt, Screenshots zu machen. Diese können anschließend mit OpenCV-Python vereint werden, um ein Video zu erstellen.

Um die entsprechenden Eye-Tracking-Daten zu erhalten, kann der Eye-Tracker vor der Aufnahme des Codes gestartet werden und nach der Aufnahme des letzten Bildes gestoppt werden. In diesem Fall ersetzt die Videoaufnahme das wait(), das normalerweise nötig ist. 

Die Initialisierung von OpenCV erfolgt genau wie bei Bild/Visualisierung.

Allerdings muss hier besonders auf die eingestellten FPS geachtet werden, da noch nicht klar ist, wie viele FPS die Aufnahme ergibt. Mehr dazu im nächsten Abschnitt

+ Zur Optimierung der Leistung können die aufgenommenen Bilder in einem anderen Thread auf den Datenspeicher geschrieben werden.

        
        # Queue die die zu schreibenden Frames enthält
        frame_queue = queue.Queue()

        # Methode wird innerhalb des unten gestarteten Threads ausgeführt
        def writer_thread_func(q, video_writer):
            while True:
                frame = q.get()
                if frame is None:
                    break  # Beenden, wenn ein Abbruchsignal (None) empfangen wird
                video_writer.write(frame)
            video_writer.release()

        # Thread für das Schreiben starten
        writer_thread = threading.Thread(target=writer_thread_func, args=(frame_queue, out))
        writer_thread.start()

+ Vor dem Starten der Bildschirmaufnahme wird der Eye-Tracker gestartet.

        # Initialisierung des Eye-Trackers fehlt hier: Siehe Abschnitt Tobii SDK
        my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

+ Mit mss werden wiederholt screenshots gemacht und anschließend in die queue gepusht. Die Abbruchbedingung ist hier ein Key-press.

        with mss.mss() as sct:
            monitor = {"top": 0, "left": 0, "width": resolution[0], "height": resolution[1]}

            while True:
                img = sct.grab(monitor)

                # Der VideoWriter akzeptiert nur Arrays. Entsprechend muss das Bild konvertiert werden.
                frame = np.array(img)[:, :, :3]

                # Frame in queue packen, sodass dieser in einem anderen Thread verarbeitet wird. 
                # Kann auch mit "out.write(frame)" direkt hier geschrieben werden, ist allerdings weniger performant.
                frame_queue.put(frame)

                # Anhalten der Aufnahme auf Druck von 'q'
                if cv2.waitKey(1) == ord('q'):
                    break

+ Anschließend wird der Eye-Tracker gestoppt und das Video gespeichert.

        #Stoppen des Eye-Trackers
        my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

        # VideoWriter releasen
        out.release()


### FPS der Aufnahme
Die Häufigkeit der Frameaufnahme kann leider nicht einfach kontrolliert werden und ist stark von der Hardware abhängig. In unseren Tests sind wir meistens nur auf etwa 25 FPS gekommen (genauer Wert schwankt von Mal zu Mal).
Für bessere Ergebnisse muss eventuell auf externe Aufnahme-Software ausgewichen werden, die über die API aus dem Code gestartet werden kann. (z.B. FFmpeg: https://pypi.org/project/python-ffmpeg/)

Alternativ können mehrere Eye-Tracking-Datenpunkte zu einem verarbeitet werden. Das kann zum Beispiel durch das Bilden des Mittelpunktes geschehen. Es können auch benachbarte Datenpunkte mit in die Berechnung einfließen.

Da die FPS bereits vor der Aufnahme angegeben werden müssen, muss die Geschwindigkeit des Videos nachträglich verändert werden. Auch das geht mit FFmpeg.
Alternativ kann das Video erneut mit opencv-python bearbeitet werden:

+ Dazu wird die tatsächliche Zahl von FPS benötigt. Diese muss parallel zur Aufnahme berechnet werden. Dann muss OpenCV mit den aktualisierten Daten erneut initialisiert werden. 

        out = cv2.VideoWriter(output_filename, fourcc, real_fps, (width, height))


+ Da OpenCV das Video immer direkt auf die Festplatte schreibt, muss die Datei erneut eingelesen werden.

        cap = cv2.VideoCapture(input_filename)
    
+ Anschließend muss jeder Frame des Videos einzeln aus der Datei ausgelesen und zur neuen Datei hinzugefügt werden.

        while cap.isOpened():
            ret, frame = cap.read()
            
            # Abbruchbedingung: Läuft so lange, bis alle Frames kopiert wurden
            if not ret:
                break
            out.write(frame)

        cap.release()
        out.release()

### Visualisierung

Die Eye-Tracker-Daten können ebenfalls mit einem Video hinterlegt werden. Das funktioniert ähnlich wie das Hinterlegen mit einem Bild.
Wichtig ist, dass das Video gleich viele Frames haben muss wie die Eye-Tracker-Blickpunkte, da jeder Frame mit genau einem Eintrag der Eye-Tracker CSV überlegt wird. Bei Unterschiedlicher Anzahl der beiden Werte "verrutscht" der Blickpunkt. Sollte das nicht der Fall sein, muss entweder die Aufnahmemethode verändert werden oder es müssen mehrere Blickpunkte zu einem Fusioniert werden.
+ Initialisierung von OpenCV
+ Frame aus Video kopieren und Eye-Tracking-Daten hinzufügen

        for (x, y) in eye_data:
            ret, frame = video_capture.read()
            if not ret:
                print("Videoende erreicht, bevor alle Blickpunkte visualisiert wurden.")
                break

            # Anschließend kann wie zuvor auf den Frame geschrieben werden:
            cv2.circle(frame, (x, y), 10, (0, 0, 255), -1)
            output_video.write(frame)
            
        # Ressourcen freigeben
        video_capture.release()
        output_video.release()

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
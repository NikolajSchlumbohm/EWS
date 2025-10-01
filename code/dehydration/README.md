Die dehydrierten Bilder dienen der Weiterverbreitung des Datensatzes ohne Urherberrecht zu verletzen. 

In Crop_data.json sind die Links zu den Bildern mir Informationen zur Bounding Box hinterlegt. 

Image_cropper_gui.py dient als Utility für das Erzeugen der crop_data_json. Diese Datei wird überschrieben, wenn image_cropper_gui ausgeführt wird. Eine Kopie der crop_data ist unter data/img/hydration_info.json.

**WICHTIG**: Die Namen der Bilder in Cropped_images und deren IDs stimmen nicht mit aktuellen IDs und Kategorien überein. Da das Bild mit ID 145 fehlte, wurden die darauffolgenden IDs um 1 dekrementiert.

Bedeutet, die IDs der Bilder mit IDs 147-153 müssen um eins reduziert, um mit den restlichen Daten übereinzustimmen
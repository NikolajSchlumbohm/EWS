import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import csv
import statistics
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np

# Achtung Chaoscode. Enthällt jeglichen Code den ich genutzt habe in einzelnen Funktionen

# Die genaueren Gruppen der Bilder mit Textinhalt sind hier Definiert:
text_hauptbestandteil = [11,12,13,16,17,128,129,130] # The text is the main part of the image. The background is not important.
text_bild_kombination = [33,88,107,108,109,110,11,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,131,132,133,134,135,136,137,138,139,140,141] # Both image and text are important.
text_hintergrund = [15,34,74,76,82,84,85,87,92,99,100,102,106,] # The text is the background of the image. The main part is the image.
nur_text = [142,143,144,146,147,148,149,150,151,152,153] # Consists only of text, no image.
all_ids = set(text_hauptbestandteil + text_bild_kombination + text_hintergrund + nur_text) # Combine all IDs into one set for fast lookup

# memes gehören aufgrund iherer Bild und textbasierter natur immer zu text_bild_kombination. Außerdem sind auch Zitate enthalten, 
# die sowohl das Zitat als auch das Bild der Person enthalten. Hier geht es nur um Zitate mit Bild der person, Zitate die lediglich mit einem namen als solches gekennzeichnet sind sind in text_hauptbestandteil enthalten.
# Demnach werden diese beiden kategorieren noch ein mal seperat betrachtet.
memes = [107,108,109,110,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127]
quotes = [33,88,131,136,138,140] 

#  Moves images from the current_images folder to the Text_pics folder, only if the image ID is in all_ids.
def move_pics():
    src_folder = r"C:/Coding/Git/EyesWideScroll/current_images"
    dst_folder = r"C:/Coding/Python_projects/Text_pics"
    for filename in os.listdir(src_folder):
        match = re.match(r"id0*([1-9]\d*)", filename)
        if not match:
            continue  # Skip files that don't match the pattern

        img_id = int(match.group(1))
        if img_id in all_ids:
            src_path = os.path.join(src_folder, filename)
            dst_path = os.path.join(dst_folder, filename)
            shutil.copy2(src_path, dst_path)

# Moves CSV files from the EyesWideScroll folder to the text_csv folder, only if the image ID is in all_ids.
def move_csv():
    src_folder = r"C:/Coding/Git/EyesWideScroll"
    dst_folder = r"C:/Coding/Python_projects/text_csv"
    for filename in os.listdir(src_folder):
        if not filename.endswith(".csv"):
            continue
        match = re.search(r"_id0*([1-9]\d*)_", filename)
        if not match:
            continue
        csv_id = int(match.group(1))
        if csv_id in all_ids:
            src_path = os.path.join(src_folder, filename)
            dst_path = os.path.join(dst_folder, filename)
            shutil.copy2(src_path, dst_path)

# Opens images from the Text_pics folder and allows the user to select areas of interest.
def get_picture_area():
    img_folder = r"D:/Git/EyesWideScroll/Text_pics"
    save_file = r"D:/Git/EyesWideScroll/areas_fake.txt"
    img_files = [f for f in os.listdir(img_folder) if re.match(r"id0*([1-9]\d*)", f)]
    img_files.sort()  # Optional: sort for consistent order

    areas_dict = {}

    class ImageSelector:
        def __init__(self, master, img_files):
            self.master = master
            self.img_files = img_files
            self.idx = 0
            self.areas = []
            self.rect = None
            self.start_x = None
            self.start_y = None
            self.img_id = None

            self.canvas = tk.Canvas(master)
            self.canvas.pack()
            self.next_btn = tk.Button(master, text="Next Image", command=self.next_image)
            self.next_btn.pack()

            self.master.bind("<Escape>", lambda e: self.master.quit())
            self.load_image()

            self.canvas.bind("<ButtonPress-1>", self.on_press)
            self.canvas.bind("<B1-Motion>", self.on_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)

        def load_image(self):
            if self.idx >= len(self.img_files):
                self.save_areas()
                self.master.quit()
                return
            self.areas = []
            img_file = self.img_files[self.idx]
            self.img_id = re.match(r"id0*([1-9]\d*)", img_file).group(1)
            img_path = os.path.join(img_folder, img_file)
            self.img = Image.open(img_path)
            self.tk_img = ImageTk.PhotoImage(self.img)
            self.canvas.config(width=self.img.width, height=self.img.height)
            self.canvas.delete("rect")
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
            self.master.geometry(f"{self.img.width}x{self.img.height+40}")

        def on_press(self, event):
            self.start_x = event.x
            self.start_y = event.y
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", tag="rect")

        def on_drag(self, event):
            if self.rect:
                self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

        def on_release(self, event):
            x0, y0 = self.start_x, self.start_y
            x1, y1 = event.x, event.y
            x_start, x_end = sorted([x0, x1])
            y_start, y_end = sorted([y0, y1])

            x_start = max(0, min(800, x_start))
            y_start = max(0, min(800, y_start))
            x_end = max(0, min(800, x_end))
            y_end = max(0, min(800, y_end))

            self.areas.append(f"({x_start},{y_start})-({x_end},{y_end})")

        def next_image(self):
            if self.areas:
                areas_str = ";".join(self.areas)
                areas_dict[self.img_id] = areas_str
            self.idx += 1
            self.canvas.delete("rect")
            self.load_image()

        def save_areas(self):
            with open(save_file, "a") as f:
                for img_id, areas_str in areas_dict.items():
                    f.write(f"{img_id}:{areas_str}\n")

    if __name__ == "__main__":
        root = tk.Tk()
        root.title("Select Areas on Images")
        selector = ImageSelector(root, img_files)
        root.mainloop()

# How many percent of the gaze points are inside the areas for each imageID. Checks every person for the given imageID.
def percentage(imageID):
    # Load areas for the given imageID
    areas_file = r"C:/Coding/Python_projects/areas.txt"
    areas = []
    with open(areas_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(str(imageID) + ":"):
                area_str = line.split(":", 1)[1]
                for area in area_str.split(";"):
                    match = re.match(r"\((\d+),(\d+)\)-\((\d+),(\d+)\)", area)
                    if match:
                        x_start, y_start, x_end, y_end = map(int, match.groups())
                        areas.append((x_start, y_start, x_end, y_end))
                break
    if not areas:
        return 0.0  # No areas found for this image

    # Find all CSV files for the imageID
    csv_folder = r"C:/Coding/Python_projects/text_csv"
    csv_files = []
    for fname in os.listdir(csv_folder):
        if re.search(r"_id0*{}[_\.]".format(imageID), fname) and fname.endswith(".csv"):
            csv_files.append(os.path.join(csv_folder, fname))
    if not csv_files:
        return 0.0  # No CSV files found
    
    # Check coordinates in all CSV files
    total = 0
    inside = 0
    for csv_file in csv_files:
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                coord = row.get("left_gaze_point_on_display_area")
                
                if not coord or "," not in coord:
                    continue
                try:
                    x, y = map(float, coord.strip("()").split(","))

                    # gaze points are in range 0-1, convert to pixel coordinates
                    x = x*800
                    y = y*800
                except ValueError as e:
                    print(e.args[0]) 
                    continue
                total += 1
                for x_start, y_start, x_end, y_end in areas:
                    if x_start < x < x_end and y_start < y < y_end:
                        inside += 1
                        break
    return (inside / total * 100) if total > 0 else 0.0

# Calculates the percentage of gaze points inside the areas for all imageIDs and writes the results to a file.
def percentage_all():
    output_file = r"C:/Coding/Python_projects/percentages.txt"
    with open(output_file, "w") as f:
        for img_id in sorted(all_ids):
            percent = percentage(img_id)
            f.write(f"{img_id}: {percent:.2f}\n")

# Similar do percentage(), but checks the positions of the fixations instead of every gaze point.
# Fixations are more stable and less noisy than gaze points, so this might yield different results
def percentage_fixations(imageID):
    # Load areas for the given imageID
    areas_file = r"C:/Coding/Python_projects/areas.txt"
    areas = []
    with open(areas_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(str(imageID) + ":"):
                area_str = line.split(":", 1)[1]
                for area in area_str.split(";"):
                    match = re.match(r"\((\d+),(\d+)\)-\((\d+),(\d+)\)", area)
                    if match:
                        x_start, y_start, x_end, y_end = map(int, match.groups())
                        areas.append((x_start, y_start, x_end, y_end))
                break
    if not areas:
        return 0.0  # No areas found for this image
    
    # Find all CSV files for the imageID
    csv_folder = r"C:/Coding/Git/EyeTracking_basti/fixations"
    csv_files = []
    for fname in os.listdir(csv_folder):
        if re.search(r"_id0*{}[_\.]".format(imageID), fname) and fname.endswith(".csv"):
            csv_files.append(os.path.join(csv_folder, fname))
    if not csv_files:
        return 0.0  # No CSV files found
    
    # Check coordinates in all CSV files
    total = 0
    inside = 0
    for csv_file in csv_files:
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                x = float(row.get("x"))
                y = float(row.get("y"))
                #coord = row.get("left_gaze_point_on_display_area")
                
                if not x or not y:
                    continue

                total += 1
                for x_start, y_start, x_end, y_end in areas:
                    if x_start < x < x_end and y_start < y < y_end:
                        inside += 1
                        break
    return (inside / total * 100) if total > 0 else 0.0

def percentage_fixations_all():
    output_file = r"C:/Coding/Python_projects/percentages_fixations.txt"
    with open(output_file, "w") as f:
        for img_id in sorted(all_ids):
            percent = percentage_fixations(img_id)
            f.write(f"{img_id}: {percent:.2f}\n")

# just some fix to the areas.txt file, so that the coordinates are always in the range 0-800. Previously, some coordinates were outside this range, which caused problems in the analysis.
def fix_area():
    check_file = r"C:/Coding/Python_projects/areas.txt"
    new_file = r"C:/Coding/Python_projects/areas_fixed.txt"
    with open(check_file, "r") as f:
        lines = f.readlines()
        fixed_lines = []
        for line in lines:
            match = re.match(r"(\d+):(.*)", line)
            if not match:
                fixed_lines.append(line)
                continue
            img_id, areas_str = match.groups()
            fixed_areas = []
            for area in areas_str.split(";"):
                coords_match = re.match(r"\((\-?\d+),(\-?\d+)\)-\((\-?\d+),(\-?\d+)\)", area)
                if coords_match:
                    x_start, y_start, x_end, y_end = map(int, coords_match.groups())
                    x_start = max(0, min(800, x_start))
                    y_start = max(0, min(800, y_start))
                    x_end = max(0, min(800, x_end))
                    y_end = max(0, min(800, y_end))
                    fixed_areas.append(f"({x_start},{y_start})-({x_end},{y_end})")
            if fixed_areas:
                fixed_lines.append(f"{img_id}:{';'.join(fixed_areas)}\n")
            else:
                fixed_lines.append(line)

        with open(new_file, "w") as f_out:
            f_out.writelines(fixed_lines)

# compares results from percentage_fixations_all() with the results from percentage_all()
# and creates a .csv file with the results
def compare():
    perc_file = r"C:/Coding/Python_projects/percentages.txt"
    fix_file = r"C:/Coding/Python_projects/percentages_fixations.txt"
    portion_file = r"C:/Coding/Python_projects/text_portion.txt"
    out_file = r"C:/Coding/Python_projects/compare_fixations.csv"

    # Read percentages.txt
    perc_dict = {}
    with open(perc_file, "r") as f:
        for line in f:
            if ":" in line:
                img_id, perc = line.strip().split(":")
                perc_dict[int(img_id)] = float(perc.strip())

    # Read percentages_fixations.txt
    fix_dict = {}
    with open(fix_file, "r") as f:
        for line in f:
            if ":" in line:
                img_id, perc = line.strip().split(":")
                fix_dict[int(img_id)] = float(perc.strip())

    # Read text_portion.txt
    portion_dict = {}
    with open(portion_file, "r") as f:
        for line in f:
            if ":" in line:
                img_id, portion = line.strip().split(":")
                portion_dict[int(img_id)] = float(portion.strip())

    # Write compare_fixations.csv
    with open(out_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "id",
            "percentage",
            "percentage_fixations",
            "difference",
            "text_portion",
            "percentage_fixations/text_portion"
        ])
        ids = sorted(perc_dict.keys())
        fix_values = []
        perc_values = []
        diff_values = []
        portion_values = []
        ratio_values = []

        for img_id in ids:
            perc = perc_dict.get(img_id, 0.0)
            fix = fix_dict.get(img_id, 0.0)
            portion = portion_dict.get(img_id, 0.0)
            diff = fix - perc
            ratio = fix / portion if portion > 0 else 0.0

            fix_values.append(fix)
            perc_values.append(perc)
            diff_values.append(diff)
            portion_values.append(portion)
            ratio_values.append(ratio)

            writer.writerow([
                img_id,
                f"{perc:.2f}",
                f"{fix:.2f}",
                f"{diff:.2f}",
                f"{portion:.4f}",
                f"{ratio:.2f}"
            ])

        # Mean row
        writer.writerow([
            "mean",
            f"{statistics.mean(perc_values):.2f}",
            f"{statistics.mean(fix_values):.2f}",
            f"{statistics.mean(diff_values):.2f}",
            f"{statistics.mean(portion_values):.4f}",
            f"{statistics.mean(ratio_values):.2f}"
        ])

        # Median row
        writer.writerow([
            "median",
            f"{statistics.median(perc_values):.2f}",
            f"{statistics.median(fix_values):.2f}",
            f"{statistics.median(diff_values):.2f}",
            f"{statistics.median(portion_values):.4f}",
            f"{statistics.median(ratio_values):.2f}"
        ])

# The groups are definded at the top of the file. This function compares the results of different values for each group. 
def compare_groups():
    compare_file = r"C:/Coding/Python_projects/compare_fixations.csv"
    out_file = r"C:/Coding/Python_projects/compare_groups.csv"

    # Read compare_fixations.csv
    data = {}
    with open(compare_file, "r", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                img_id = int(row["id"])
            except ValueError:
                continue  # skip mean/median rows
            data[img_id] = {
                "percentage": float(row["percentage"]),
                "percentage_fixations": float(row["percentage_fixations"]),
                "difference": float(row["difference"]),
                "text_portion": float(row["text_portion"]),
                "percentage_fixations/text_portion": float(row["percentage_fixations/text_portion"])
            }

    groups = {
        "text_hauptbestandteil": text_hauptbestandteil,
        "text_bild_kombination": text_bild_kombination,
        "-memes": memes,
        "-quotes": quotes,
        "text_hintergrund": text_hintergrund,
        "nur_text": nur_text
    }

    with open(out_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        # First: mean section
        writer.writerow([
            "group",
            "mean percentage",
            "var percentage",
            "mean percentage_fixations",
            "var percentage_fixations",
            "mean difference",
            "mean text_portion",
            "var text_portion",
            "mean percentage_fixations/text_portion",
            "var percentage_fixations/text_portion"
        ])
        for group_name, ids in groups.items():
            perc_values = [data.get(img_id, {}).get("percentage", 0.0) for img_id in ids]
            fix_values = [data.get(img_id, {}).get("percentage_fixations", 0.0) for img_id in ids]
            diff_values = [data.get(img_id, {}).get("difference", 0.0) for img_id in ids]
            text_portion_values = [data.get(img_id, {}).get("text_portion", 0.0) for img_id in ids]
            ratio_values = [data.get(img_id, {}).get("percentage_fixations/text_portion", 0.0) for img_id in ids]

            mean_perc = statistics.mean(perc_values) if perc_values else 0.0
            var_perc = statistics.variance(perc_values) if len(perc_values) > 1 else 0.0
            mean_fix = statistics.mean(fix_values) if fix_values else 0.0
            var_fix = statistics.variance(fix_values) if len(fix_values) > 1 else 0.0
            mean_diff = statistics.mean(diff_values) if diff_values else 0.0
            mean_text_portion = statistics.mean(text_portion_values) if text_portion_values else 0.0
            var_text_portion = statistics.variance(text_portion_values) if len(text_portion_values) > 1 else 0.0
            mean_ratio = statistics.mean(ratio_values) if ratio_values else 0.0
            var_ratio = statistics.variance(ratio_values) if len(ratio_values) > 1 else 0.0

            writer.writerow([
                group_name,
                f"{mean_perc:.2f}",
                f"{var_perc:.2f}",
                f"{mean_fix:.2f}",
                f"{var_fix:.2f}",
                f"{mean_diff:.2f}",
                f"{mean_text_portion:.4f}",
                f"{var_text_portion:.4f}",
                f"{mean_ratio:.2f}",
                f"{var_ratio:.2f}"
            ])

        # Empty row
        writer.writerow([])

        # Second: median section
        writer.writerow([
            "group",
            "median percentage",
            "var percentage (median)",
            "median percentage_fixations",
            "var percentage_fixations (median)",
            "median difference",
            "median text_portion",
            "var text_portion (median)",
            "median percentage_fixations/text_portion",
            "var percentage_fixations/text_portion (median)"
        ])
        for group_name, ids in groups.items():
            perc_values = [data.get(img_id, {}).get("percentage", 0.0) for img_id in ids]
            fix_values = [data.get(img_id, {}).get("percentage_fixations", 0.0) for img_id in ids]
            diff_values = [data.get(img_id, {}).get("difference", 0.0) for img_id in ids]
            text_portion_values = [data.get(img_id, {}).get("text_portion", 0.0) for img_id in ids]
            ratio_values = [data.get(img_id, {}).get("percentage_fixations/text_portion", 0.0) for img_id in ids]

            median_perc = statistics.median(perc_values) if perc_values else 0.0
            var_perc_median = statistics.variance(perc_values) if len(perc_values) > 1 else 0.0
            median_fix = statistics.median(fix_values) if fix_values else 0.0
            var_fix_median = statistics.variance(fix_values) if len(fix_values) > 1 else 0.0
            median_diff = statistics.median(diff_values) if diff_values else 0.0
            median_text_portion = statistics.median(text_portion_values) if text_portion_values else 0.0
            var_text_portion_median = statistics.variance(text_portion_values) if len(text_portion_values) > 1 else 0.0
            median_ratio = statistics.median(ratio_values) if ratio_values else 0.0
            var_ratio_median = statistics.variance(ratio_values) if len(ratio_values) > 1 else 0.0

            writer.writerow([
                group_name,
                f"{median_perc:.2f}",
                f"{var_perc_median:.2f}",
                f"{median_fix:.2f}",
                f"{var_fix_median:.2f}",
                f"{median_diff:.2f}",
                f"{median_text_portion:.4f}",
                f"{var_text_portion_median:.4f}",
                f"{median_ratio:.2f}",
                f"{var_ratio_median:.2f}"
            ])

# Calculates the portion of the image that is text for a given imageID.
def text_portion(imageID):

    areas_file = r"C:/Coding/Python_projects/areas.txt"
    total_area = 800 * 800
    text_area = 0

    with open(areas_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(str(imageID) + ":"):
                area_str = line.split(":", 1)[1]
                for area in area_str.split(";"):
                    match = re.match(r"\((\d+),(\d+)\)-\((\d+),(\d+)\)", area)
                    if match:
                        x_start, y_start, x_end, y_end = map(int, match.groups())
                        width = abs(x_end - x_start)
                        height = abs(y_end - y_start)
                        text_area += width * height
                break

    portion = text_area / total_area if total_area > 0 else 0.0
    return portion

# Calculates the text portion for all imageIDs and writes the results to a file.
def text_portion_all():
    output_file = r"C:/Coding/Python_projects/text_portion.txt"
    with open(output_file, "w") as f:
        for img_id in sorted(all_ids):
            portion = text_portion(img_id)
            f.write(f"{img_id}: {portion:.4f}\n")

def fixation_timing():
    areas_file = r"C:/Coding/Python_projects/areas.txt"
    fix_folder = r"C:/Coding/Git/EyeTracking_basti/fixations"
    output_file = r"C:/Coding/Python_projects/fixation_timing.csv"

    # Load areas for all imageIDs
    areas_dict = {}
    with open(areas_file, "r") as f:
        for line in f:
            line = line.strip()
            match = re.match(r"(\d+):(.*)", line)
            if not match:
                continue
            img_id, areas_str = match.groups()
            areas = []
            for area in areas_str.split(";"):
                coords_match = re.match(r"\((\d+),(\d+)\)-\((\d+),(\d+)\)", area)
                if coords_match:
                    x_start, y_start, x_end, y_end = map(int, coords_match.groups())
                    areas.append((x_start, y_start, x_end, y_end))
            if areas:
                areas_dict[int(img_id)] = areas

    # For each imageID, collect all fixations for each file and check if they're in area
    results = {}  # {img_id: [[0/1, 0/1, ...], ...]}
    max_fix_count = {}  # {img_id: max number of fixations found}
    for fix_file in glob.glob(os.path.join(fix_folder, "*.csv")):
        fname = os.path.basename(fix_file)
        match = re.search(r"_id0*([1-9]\d*)[_\.]", fname)
        if not match:
            continue
        img_id = int(match.group(1))
        if img_id not in areas_dict:
            continue
        areas = areas_dict[img_id]
        fix_in_area = []
        with open(fix_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    x = float(row.get("x"))
                    y = float(row.get("y"))
                except (TypeError, ValueError):
                    in_area = 0
                else:
                    in_area = 0
                    for x_start, y_start, x_end, y_end in areas:
                        if x_start < x < x_end and y_start < y < y_end:
                            in_area = 1
                            break
                fix_in_area.append(in_area)
        if img_id not in results:
            results[img_id] = []
            max_fix_count[img_id] = 0
        results[img_id].append(fix_in_area)
        if len(fix_in_area) > max_fix_count[img_id]:
            max_fix_count[img_id] = len(fix_in_area)

    # Calculate percentage for each fixation index for each imageID
    with open(output_file, "w", newline='') as csvfile:
        # Write header: id | fixation 1 | fixation 2 | ...
        max_fix = max(max_fix_count.values()) if max_fix_count else 0
        headers = ["id"] + [f"fixation {i+1}" for i in range(max_fix)]
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        # Collect all percentages for each fixation index for stats
        all_percentages = [[] for _ in range(max_fix)]
        for img_id in sorted(results.keys()):
            fix_lists = results[img_id]
            row = [img_id]
            for i in range(max_fix_count[img_id]):
                values = [fix[i] for fix in fix_lists if len(fix) > i]
                percent = (sum(values) / len(values) * 100) if values else 0.0
                row.append(f"{percent:.2f}")
                if i < max_fix:
                    all_percentages[i].append(percent)
            writer.writerow(row)
        # Add mean, median, var rows
        mean_row = ["mean"]
        median_row = ["median"]
        var_row = ["var"]
        for col in all_percentages:
            mean_row.append(f"{statistics.mean(col):.2f}" if col else "")
            median_row.append(f"{statistics.median(col):.2f}" if col else "")
            var_row.append(f"{statistics.variance(col):.2f}" if len(col) > 1 else "")
        writer.writerow(mean_row)
        writer.writerow(median_row)
        writer.writerow(var_row)

def timing():
    areas_file = r"D:/Git/EyesWideScroll/areas.txt"
    gaze_folder = r"D:/Git/EyesWideScroll/text_csv"
    output_file = r"D:/Git/EyesWideScroll/gaze_timing.csv"

    # Load areas for all imageIDs
    areas_dict = {}
    with open(areas_file, "r") as f:
        for line in f:
            line = line.strip()
            match = re.match(r"(\d+):(.*)", line)
            if not match:
                continue
            img_id, areas_str = match.groups()
            areas = []
            for area in areas_str.split(";"):
                coords_match = re.match(r"\((\d+),(\d+)\)-\((\d+),(\d+)\)", area)
                if coords_match:
                    x_start, y_start, x_end, y_end = map(int, coords_match.groups())
                    areas.append((x_start, y_start, x_end, y_end))
            if areas:
                areas_dict[int(img_id)] = areas

    # For each imageID, collect all gaze point lists (one per proband)
    results = {}  # {img_id: [[0/1, 0/1, ...], ...]}
    max_point_count = {}  # {img_id: max number of gaze points found}
    for gaze_file in glob.glob(os.path.join(gaze_folder, "*.csv")):
        fname = os.path.basename(gaze_file)
        match = re.search(r"_id0*([1-9]\d*)[_\.]", fname)
        if not match:
            continue
        img_id = int(match.group(1))
        if img_id not in areas_dict:
            continue
        areas = areas_dict[img_id]
        gaze_in_area = []
        with open(gaze_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                coord = row.get("left_gaze_point_on_display_area")
                if not coord or "," not in coord:
                    gaze_in_area.append(0)
                    continue
                try:
                    x, y = map(float, coord.strip("()").split(","))
                    x = x * 800
                    y = y * 800
                except Exception:
                    gaze_in_area.append(0)
                    continue
                in_area = 0
                for x_start, y_start, x_end, y_end in areas:
                    if x_start < x < x_end and y_start < y < y_end:
                        in_area = 1
                        break
                gaze_in_area.append(in_area)
        if img_id not in results:
            results[img_id] = []
            max_point_count[img_id] = 0
        results[img_id].append(gaze_in_area)
        if len(gaze_in_area) > max_point_count[img_id]:
            max_point_count[img_id] = len(gaze_in_area)

    # Calculate percentage for each gaze point index for each imageID
    with open(output_file, "w", newline='') as csvfile:
        # Write header: image_id | first point | second point | ...
        max_point = max(max_point_count.values()) if max_point_count else 0
        headers = ["image_id"] + [f"point {i+1}" for i in range(max_point)]
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for img_id in sorted(results.keys()):
            gaze_lists = results[img_id]
            row = [img_id]
            for i in range(max_point_count[img_id]):
                values = [gaze[i] for gaze in gaze_lists if len(gaze) > i]
                percent = (sum(values) / len(values) * 100) if values else 0.0
                row.append(f"{percent:.2f}")
            writer.writerow(row)

def group_timing():
    gaze_timing_file = r"D:/Git/EyesWideScroll/gaze_timing.csv"
    out_file = r"D:/Git/EyesWideScroll/grouped_gaze_timing.csv"

    # Read gaze_timing.csv
    data = {}
    with open(gaze_timing_file, "r", newline='') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            try:
                img_id = int(row["image_id"])
            except ValueError:
                continue  # skip non-numeric rows
            data[img_id] = [float(row[h]) for h in headers[1:] if row[h]]

    groups = {
        "text_hauptbestandteil": text_hauptbestandteil,
        "text_bild_kombination": text_bild_kombination,
        "-memes": memes,
        "-quotes": quotes,
        "text_hintergrund": text_hintergrund,
        "nur_text": nur_text
    }

    # Determine max number of gaze points
    max_points = max((len(vals) for vals in data.values()), default=0)

    with open(out_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Header
        header = ["group"] + [f"point{i+1}_mean" for i in range(max_points)]
        writer.writerow(header)

        for group_name, ids in groups.items():
            # Collect gaze values for each point index
            point_lists = [[] for _ in range(max_points)]
            for img_id in ids:
                vals = data.get(img_id, [])
                for i in range(len(vals)):
                    point_lists[i].append(vals[i])
            row = [group_name]
            for point_vals in point_lists:
                if point_vals:
                    row.append(f"{statistics.mean(point_vals):.2f}")
                else:
                    row.append("")
            writer.writerow(row)

def timing_groups():

    timing_file = r"C:/Coding/Python_projects/fixation_timing.csv"
    out_file = r"C:/Coding/Python_projects/timing_groups.csv"

    # Read fixation_timing.csv
    data = {}
    with open(timing_file, "r", newline='') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            try:
                img_id = int(row["id"])
            except ValueError:
                continue  # skip mean/median/var rows
            data[img_id] = [float(row[h]) for h in headers[1:] if row[h]]

    groups = {
        "text_hauptbestandteil": text_hauptbestandteil,
        "text_bild_kombination": text_bild_kombination,
        "-memes": memes,
        "-quotes": quotes,
        "text_hintergrund": text_hintergrund,
        "nur_text": nur_text
    }

    # Determine max number of fixations
    max_fix = max((len(vals) for vals in data.values()), default=0)

    with open(out_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Header
        header = ["group"]
        for i in range(max_fix):
            header += [f"fix{i+1}_mean", f"fix{i+1}_median", f"fix{i+1}_var"]
        writer.writerow(header)

        for group_name, ids in groups.items():
            # Collect fixation values for each fixation index
            fix_lists = [[] for _ in range(max_fix)]
            for img_id in ids:
                vals = data.get(img_id, [])
                for i in range(len(vals)):
                    fix_lists[i].append(vals[i])
            row = [group_name]
            for fix_vals in fix_lists:
                if fix_vals:
                    row.append(f"{statistics.mean(fix_vals):.2f}")
                    row.append(f"{statistics.median(fix_vals):.2f}")
                    row.append(f"{statistics.variance(fix_vals):.2f}" if len(fix_vals) > 1 else "0.00")
                else:
                    row += ["", "", ""]
            writer.writerow(row)

def show_group_percentages():
    csv_file = r"C:/Coding/Python_projects/compare_groups.csv"
    groups = []
    mean_percentage = []
    mean_percentage_fixations = []

    # Read only the first section (mean rows) from the CSV
    with open(csv_file, "r", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0] == "":  # Stop at empty row (before median section)
                break
            groups.append(row[0])
            mean_percentage.append(float(row[1]))
            mean_percentage_fixations.append(float(row[3]))

    x = range(len(groups))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar([i - width/2 for i in x], mean_percentage, width, label='Mean Percentage', color='skyblue')
    ax.bar([i + width/2 for i in x], mean_percentage_fixations, width, label='Mean Percentage Fixations', color='orange')

    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=45, ha='right')
    ax.set_ylabel('Percentage')
    ax.set_title('Mean Percentage vs Mean Percentage Fixations by Group')
    ax.legend()
    plt.tight_layout()
    plt.show()

def show_group_portion():
    csv_file = r"D:/Git/EyesWideScroll/compare_groups.csv"
    groups = []
    mean_text_portion = []

    # Read only the first section (mean rows) from the CSV
    with open(csv_file, "r", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0] == "":
                break
            groups.append(row[0])
            mean_text_portion.append(float(row[6]))

    x = range(len(groups))
    width = 0.5

    fig, ax = plt.subplots()
    # Use the variable name as the label
    ax.bar(x, mean_text_portion, width, label='mean_text_portion', color='lightgreen')

    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=45, ha='right')
    ax.set_ylabel('Text Portion')
    ax.set_title('Mean Text Portion by Group')
    ax.legend()
    plt.tight_layout()
    plt.show()

def  show_group_portion_variance():
    csv_file = r"D:/Git/EyesWideScroll/compare_groups.csv"
    groups = []
    mean_text_portion = []
    var_text_portion = []

    # Read only the first section (mean rows) from the CSV
    with open(csv_file, "r", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0] == "":
                break
            groups.append(row[0])
            mean_text_portion.append(float(row[6]))
            var_text_portion.append(float(row[7]))

    x = range(len(groups))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar([i - width/2 for i in x], mean_text_portion, width, label='Mean Text Portion', color='lightgreen')
    ax.bar([i + width/2 for i in x], var_text_portion, width, label='Variance Text Portion', color='salmon')

    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=45, ha='right')
    ax.set_ylabel('Text Portion')
    ax.set_title('Mean and Variance of Text Portion by Group')
    ax.legend()
    plt.tight_layout()
    plt.show()

def show_grouped_fixation_timing():
    csv_file = r"C:/Coding/Python_projects/timing_groups.csv"
    df = pd.read_csv(csv_file)
    # Only use group rows (skip mean/median/var if present)
    group_rows = df[~df['group'].isin(['mean', 'median', 'var'])]

    # Find all fixation columns with '_median' in their name
    fixation_median_cols = [col for col in df.columns if '_median' in col]

    fig, ax = plt.subplots()
    for idx, row in group_rows.iterrows():
        medians = [float(row[col]) if row[col] != "" else 0.0 for col in fixation_median_cols]
        ax.plot(range(1, len(medians)+1), medians, marker='o', label=row['group'])

    ax.set_xlabel('Fixation Number')
    ax.set_ylabel('Median Percentage in Area')
    ax.set_title('Median Percentage in Area by Fixation and Group')
    ax.legend()
    plt.tight_layout()
    plt.show()

def show_fixation_text_portion():
    csv_file = r"D:/Git/EyesWideScroll/compare_fixations.csv"
    df = pd.read_csv(csv_file)

    # Remove rows where id is not a number (mean/median rows)
    df = df[pd.to_numeric(df['id'], errors='coerce').notnull()]

    # Convert columns to float
    df['percentage_fixations'] = df['percentage_fixations'].astype(float)
    df['text_portion'] = df['text_portion'].astype(float)

    plt.figure(figsize=(8, 6))
    plt.scatter(df['text_portion'], df['percentage_fixations'], color='purple', alpha=0.7)
    plt.xlabel('Text Portion')
    plt.ylabel('Percentage Fixations')
    plt.title('Percentage Fixations vs Text Portion')
    plt.grid(True)
    # Draw a straight red line from (0,0) to (1,1)
    plt.plot([0, 1], [0, 1], color='red', linewidth=2)

    # Normalize x axis to 1 and divide y axis values by 100
    plt.scatter(df['text_portion'], df['percentage_fixations'] / 100, color='purple', alpha=0.7)
    plt.xlabel('Text Portion')
    plt.ylabel('Percentage Fixations')
    plt.title('Percentage Fixations vs Text Portion')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.grid(True)
    # Draw a straight red line from (0,0) to (1,1)
    plt.plot([0, 1], [0, 1], color='red', linewidth=2)
    plt.tight_layout()
    plt.show()

def show_grouped_fixation_text_portion():
    csv_file = r"D:/Git/EyesWideScroll/compare_groups.csv"
    groups = []
    mean_percentage_fixations = []
    mean_text_portion = []

    # Read only the first section (mean rows) from the CSV
    with open(csv_file, "r", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0] == "":
                break
            groups.append(row[0])
            mean_percentage_fixations.append(float(row[3]))
            mean_text_portion.append(float(row[6]) * 100)  # convert to percent for comparison

    # Calculate averages
    avg_fix = sum(mean_percentage_fixations) / len(mean_percentage_fixations) if mean_percentage_fixations else 0
    avg_portion = sum(mean_text_portion) / len(mean_text_portion) if mean_text_portion else 0

    # Add "Average" bar
    groups.append("Average")
    mean_percentage_fixations.append(avg_fix)
    mean_text_portion.append(avg_portion)

    x = range(len(groups))
    width = 0.35

    fig, ax = plt.subplots()
    # Normal bars
    ax.bar([i - width/2 for i in x[:-1]], mean_percentage_fixations[:-1], width, label='Mean text focus percentage', color='orange')
    ax.bar([i + width/2 for i in x[:-1]], mean_text_portion[:-1], width, label='Mean text portion', color='lightgreen')
    # Average bar (grayish)
    ax.bar(x[-1] - width/2, mean_percentage_fixations[-1], width, color='gray', label='Average (focus %)' if len(groups) == 1 else None, alpha=0.7)
    ax.bar(x[-1] + width/2, mean_text_portion[-1], width, color='darkgray', label='Average (portion)' if len(groups) == 1 else None, alpha=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=45, ha='right')
    ax.set_ylabel('Percentage')
    ax.set_title('Mean text focus percentage vs mean text portion by Group')
    ax.legend()
    plt.tight_layout()
    plt.show()

def show_group_timings():
    """
    Plots the mean percentage in area over time (gaze points) for each group,
    using the data from grouped_gaze_timing.csv.
    Also plots the average over all groups as a dark gray, slightly transparent line behind the others.
    """
    csv_file = r"D:/Git/EyesWideScroll/grouped_gaze_timing.csv"
    import matplotlib.pyplot as plt

    df = pd.read_csv(csv_file)
    # Only use group rows (skip mean/median/var if present)
    group_rows = df[~df['group'].isin(['mean', 'median', 'var'])]

    # Find all columns that represent time points (pointX_mean)
    time_cols = [col for col in df.columns if col.startswith('point') and col.endswith('_mean')]

    fig, ax = plt.subplots()
    all_values = []
    # Plot average first, so it's behind
    for idx, row in group_rows.iterrows():
        values = [float(row[col]) if row[col] != "" else 0.0 for col in time_cols]
        all_values.append(values)
    if all_values:
        avg = np.mean(all_values, axis=0)
        ax.plot(
            range(1, len(avg)+1),
            avg,
            color='dimgray',
            alpha=0.8,
            label='Average',
            zorder=1
        )
    # Plot groups
    for idx, row in group_rows.iterrows():
        values = [float(row[col]) if row[col] != "" else 0.0 for col in time_cols]
        ax.plot(
            range(1, len(values)+1),
            values,
            label=row['group'],
            zorder=2
        )

    ax.set_xlabel('Gaze Point Number')
    ax.set_ylabel('Mean Percentage in Area')
    ax.set_title('Mean Percentage in Area Over Time by Group')
    ax.legend()
    plt.tight_layout()
    plt.show()

def show_fixation_text_portion_grouped():
    """
    Plots a scatter plot of mean percentage fixations vs mean text portion for each group,
    using the data from compare_groups.csv.
    """
    csv_file = r"D:/Git/EyesWideScroll/compare_groups.csv"
    groups = []
    mean_percentage_fixations = []
    mean_text_portion = []

    # Read only the first section (mean rows) from the CSV
    with open(csv_file, "r", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0] == "":
                break
            groups.append(row[0])
            mean_percentage_fixations.append(float(row[3]))
            mean_text_portion.append(float(row[6]) * 100)  # convert to percent for comparison

    plt.figure(figsize=(8, 6))
    plt.scatter(mean_text_portion, mean_percentage_fixations, color='purple', alpha=0.7)

    # Annotate each point with the group name
    for i, group in enumerate(groups):
        plt.annotate(group, (mean_text_portion[i], mean_percentage_fixations[i]), textcoords="offset points", xytext=(5,5), ha='left', fontsize=9)

    plt.xlabel('Mean Text Portion (%)')
    plt.ylabel('Mean Percentage Fixations (%)')
    plt.title('Mean Percentage Fixations vs Mean Text Portion by Group')
    plt.grid(True)
    # Draw a straight red line from (0,0) to (100,100)
    plt.plot([0, 100], [0, 100], color='red', linewidth=2)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()

def show_fixation_dev_text_portion_grouped():
    """
    Plots a bar chart of mean (percentage_fixations/100)/text_portion for each group,
    using the data from compare_groups.csv.
    """
    csv_file = r"D:/Git/EyesWideScroll/compare_groups.csv"
    groups = []
    mean_percentage_fixations = []
    mean_text_portion = []
    mean_ratio = []

    # Read only the first section (mean rows) from the CSV
    with open(csv_file, "r", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0] == "":
                break
            groups.append(row[0])
            mean_percentage_fixations.append(float(row[3]))
            mean_text_portion.append(float(row[6]))

    # Compute (mean_percentage_fixations/100) / mean_text_portion
    for perc, portion in zip(mean_percentage_fixations, mean_text_portion):
        ratio = (perc / 100) / portion if portion > 0 else 0.0
        mean_ratio.append(ratio)

    x = range(len(groups))
    width = 0.5

    plt.figure(figsize=(8, 6))
    plt.bar(x, mean_ratio, width, color='cornflowerblue')
    plt.xticks(x, groups, rotation=45, ha='right')
    plt.ylabel('Mean percentage_fixations / text_portion')
    plt.title('Mean percentage_fixations / text_portion by Group')
    plt.tight_layout()
    plt.show()

def show_fixation_text_portion_grouped():
    """
    Plots a scatter plot of percentage_fixations vs text_portion for each image,
    colored/grouped by the defined groups. If an image is in memes or quotes,
    it is shown as such, otherwise by its main group.
    """
    import matplotlib.pyplot as plt

    # Read data from compare_fixations.csv
    csv_file = r"D:/Git/EyesWideScroll/compare_fixations.csv"
    df = pd.read_csv(csv_file)

    # Remove rows where id is not a number (mean/median rows)
    df = df[pd.to_numeric(df['id'], errors='coerce').notnull()]
    df['id'] = df['id'].astype(int)
    df['percentage_fixations'] = df['percentage_fixations'].astype(float)
    df['text_portion'] = df['text_portion'].astype(float)

    # Assign group for each id
    group_labels = []
    for img_id in df['id']:
        if img_id in memes:
            group_labels.append('memes')
        elif img_id in quotes:
            group_labels.append('quotes')
        elif img_id in text_hauptbestandteil:
            group_labels.append('text_hauptbestandteil')
        elif img_id in text_bild_kombination:
            group_labels.append('text_bild_kombination')
        elif img_id in text_hintergrund:
            group_labels.append('text_hintergrund')
        elif img_id in nur_text:
            group_labels.append('nur_text')
        else:
            group_labels.append('other')
    df['group'] = group_labels

    # Define colors for each group
    group_color_map = {
        'memes': 'red',
        'quotes': 'orange',
        'text_hauptbestandteil': 'blue',
        'text_bild_kombination': 'green',
        'text_hintergrund': 'purple',
        'nur_text': 'brown',
        'other': 'gray'
    }

    plt.figure(figsize=(8, 6))
    for group, color in group_color_map.items():
        group_df = df[df['group'] == group]
        if not group_df.empty:
            plt.scatter(
                group_df['text_portion'],
                group_df['percentage_fixations'] / 100,
                color=color,
                alpha=0.7,
                label=group
            )

    plt.xlabel('Text Portion')
    plt.ylabel('Percentage Fixations')
    plt.title('Percentage Fixations vs Text Portion (Grouped)')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.grid(True)
    plt.plot([0, 1], [0, 1], color='black', linewidth=2, linestyle='--')
    plt.legend()
    plt.tight_layout()
    plt.show()

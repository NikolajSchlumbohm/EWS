import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os
import json


CROPPED_DIR = "cropped_images"
LOG_FILE = "crop_data.json"

os.makedirs(CROPPED_DIR, exist_ok=True)

class ImageCropperApp:
    
    def __init__(self, master, url_file):
        self.master = master
        self.master.title("Image Cropper")

        self.canvas = tk.Canvas(master, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)


        self.urls = self.load_urls(url_file)
        self.current_index = 0
        self.crop_size = 100
        self.crop_offset = [0, 0]

        self.image = None
        self.tk_image = None
        self.crop_rect = None
        # Linkklick zum Verschieben des Crop-Rechtecks
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        # Mousescroll zum Vergrößern/Verkleinern des Crop-Rechtecks
        self.master.bind("<MouseWheel>", self.on_mousewheel)
        # Rechtsklick zum Speichern und zum nächsten Bild
        self.master.bind("<Button-3>", lambda e: self.save_crop_and_next())

        self.load_image()

        
        self.done_button = tk.Button(master, text="Done", command=self.save_crop_and_next)
        self.done_button.pack(side=tk.BOTTOM, pady=10)

        self.log_data = []

    def load_urls(self, url_file):
        with open(url_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    def load_image(self):
        if self.current_index >= len(self.urls):
            self.finish()
            return

        url = self.urls[self.current_index]
        try:
            response = requests.get(url)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            self.original_image = Image.open(image_data).convert("RGB")
        except Exception as e:
            messagebox.showerror("Error", f"Bild konnte nicht geladen werden: {url}\n{e}")
            self.current_index += 1
            self.load_image()
            return

        # Resize for display
        screen_w, screen_h = 1000, 700
        img_w, img_h = self.original_image.size
        scale_w = screen_w / img_w
        scale_h = screen_h / img_h
        self.scale = min(scale_w, scale_h, 1.0)

        display_size = (int(img_w * self.scale), int(img_h * self.scale))
        self.display_image = self.original_image.resize(display_size, Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        self.canvas.config(width=display_size[0], height=display_size[1])
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        self.crop_offset = [0, 0]
        self.crop_size = min(100, display_size[0], display_size[1])
        self.draw_crop_box()

    def draw_crop_box(self):
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        x, y = self.crop_offset
        size = self.crop_size
        self.crop_rect = self.canvas.create_rectangle(x, y, x + size, y + size, outline="red", width=2)

    def on_mousewheel(self, event):
        # Resize the crop box
        delta = 10 if event.delta > 0 else -10
        self.crop_size = max(10, self.crop_size + delta)
        self.draw_crop_box()
    def on_click(self, event):
        self.crop_offset = [event.x, event.y]
        self.draw_crop_box()

    def on_drag(self, event):
        self.crop_offset = [event.x, event.y]
        self.draw_crop_box()

    def save_crop_and_next(self):
        dx, dy = self.crop_offset
        dsize = self.crop_size

        # Convert display coordinates to original image coordinates
        scale = self.scale
        x = int(dx / scale)
        y = int(dy / scale)
        size = int(dsize / scale)

        # Clamp coordinates to image boundaries
        img_w, img_h = self.original_image.size
        x = max(0, min(x, img_w - size))
        y = max(0, min(y, img_h - size))

        cropped = self.original_image.crop((x, y, x + size, y + size))
        url = self.urls[self.current_index]

        filename = f"cropped_{self.current_index}.jpg"
        filepath = os.path.join(CROPPED_DIR, filename)
        cropped.save(filepath)

        self.log_data.append({
            "url": url,
            "offset": {"x": x, "y": y},
            "size": size,
            "cropped_file": filename
        })

        with open(LOG_FILE, "w") as f:
            json.dump(self.log_data, f, indent=2)

        self.current_index += 1
        self.load_image()
        
    def finish(self):
        messagebox.showinfo("Done", "Alle Bilder wurden bearbeitet.")
        self.master.quit()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Nutzweise: python image_cropper_gui.py image_urls.txt")
        sys.exit(1)

    root = tk.Tk()
    app = ImageCropperApp(root, sys.argv[1])
    root.mainloop()
"""
# rms_per_image.py
# Zweck
Berechnet für **alle Bilder** den **RMS-Kontrast** (Standardabweichung der Grauintensitäten in [0,1])
und speichert eine CSV mit einem Wert pro Bild.

# Eingaben
- Bildordner (rekursiv): *.jpg, *.jpeg, *.png
- Optional: 5-Bit-Maske im Dateinamen (…_xxxxx), Bits in Reihenfolge:
  ["meme", "ort", "person", "politik", "text"]  → z. B. 10100

# Ausgaben
- CSV: `rms_per_file.csv` mit mindestens:
  - `stem`            – Dateiname ohne Erweiterung
  - `rms_contrast`    – RMS-Kontrast des Bildes in [0,1]
  (Optional können zusätzliche Spalten wie `file_image`, `mask`, `label` enthalten sein, falls im Code aktiv.)

# CLI / Pfade
--input  / -i : Eingabeordner (repo-relativ oder absolut), Default: EWS/data/img/img_bin
--out    / -o : Output-Ordner  (repo-relativ oder absolut), Default: EWS/code/kontraste/rms_per_image
--per-file-csv : Dateiname der Ausgabedatei, Default: rms_per_file.csv

# Beispiel
python rms_per_image.py -i EWS/data/img/img_bin -o EWS/code/kontraste/rms_per_image

# Hinweise
- RMS = std(I), I in [0,1]; misst globale Helligkeits-Kontraste (frequenz- und ortsunabhängig).
- Die 5-Bit-Maske ist **optional** und wird nur extrahiert, wenn im Dateinamen vorhanden.
"""


from pathlib import Path
import argparse, os, sys
import numpy as np
import pandas as pd
from skimage import io, color

# --------------------------------------------------------------------------------------
# CLI / Pfade
# --------------------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="RMS-Kontrast pro Bild (minimal)")
    p.add_argument("--input","-i",
                   default=os.environ.get("EWS_INPUT_DIR", "EWS/data/img/img_bin"),
                   help="Bilder-Ordner (repo-relativ oder absolut).")
    p.add_argument("--out","-o",
                   default=os.environ.get("EWS_OUT_DIR", "EWS/code/kontraste/rms_per_image"),
                   help="Output-Ordner (repo-relativ oder absolut).")
    return p.parse_args()

ARGS = parse_args()

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parents[2] if len(SCRIPT_DIR.parents) >= 2 else SCRIPT_DIR

def R(pth: str, root: Path) -> Path:
    p = Path(pth)
    return p if p.is_absolute() else (root / p)

IN_DIR  = R(ARGS.input, REPO_ROOT).resolve()
OUT_DIR = R(ARGS.out,   REPO_ROOT).resolve()
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"[Info] RepoRoot: {REPO_ROOT}")
print(f"[Info] Input   : {IN_DIR}")
print(f"[Info] Output  : {OUT_DIR}")

# --- Bildlader: Graustufe [0,1] ---
def load_gray01(path: Path) -> np.ndarray:
    img = io.imread(path)
    if img.ndim == 2:
        g = img.astype(np.float32)
        if g.max() > 1.0: g /= 255.0
        return g
    if img.ndim == 3:
        if img.shape[2] > 3:
            img = img[..., :3]
        img = img.astype(np.float32)
        if img.max() > 1.0: img /= 255.0
        return color.rgb2gray(img).astype(np.float32)
    raise ValueError(f"Unsupported image shape: {img.shape}")

def rms_contrast(gray01: np.ndarray) -> float:
    return float(np.std(gray01, ddof=0))

# --- Bilder suchen ---
image_paths = sorted({
    p for ext in ("*.jpg","*.jpeg","*.png","*.bmp","*.tif","*.tiff")
    for p in IN_DIR.rglob(ext)
})
if not image_paths:
    sys.exit(f"Keine Bilder gefunden in: {IN_DIR}")

# --- Loop & CSV ---
rows = []
for p in image_paths:
    try:
        g = load_gray01(p)
        rms = rms_contrast(g)
       
        rows.append({
            "stem": p.stem,
            "rms_contrast": rms
        })
    except Exception as e:
        print(f"[Warnung] {p.name}: {e}")

df = pd.DataFrame(rows).sort_values("stem")

if df.empty:
    sys.exit("Keine auswertbaren Bilder.")

out_csv = OUT_DIR / "rms_per_file.csv"
df.to_csv(out_csv, index=False)
print(f"[OK] RMS-CSV gespeichert: {out_csv}")
print(df.head(10))

"""
# laplace_per_image.py
# Zweck
Berechnet für **alle Bilder** die **normalisierte Laplace-Varianz** (Kanten-/Feinkontrast-Metrik)
und speichert eine CSV mit einem Wert pro Bild.

# Eingaben
- Bildordner (rekursiv): *.jpg, *.jpeg, *.png
- Optional: 5-Bit-Maske im Dateinamen (…_xxxxx), Bits in Reihenfolge:
  ["meme", "ort", "person", "politik", "text"]  → z. B. 10100

# Ausgaben
- CSV: `laplace_per_file.csv` mit mindestens:
  - `stem`           – Dateiname ohne Erweiterung
  - `lap_var_norm`   – normalisierte Laplace-Varianz (var(L) / (var(I_smooth)+eps))
  (Optional können zusätzliche Spalten wie `file_image`, `mask`, `label` enthalten sein, falls im Code aktiv.)

# CLI / Pfade & Parameter
--input-img      : Eingabeordner (repo-relativ oder absolut), Default: EWS/data/img/img_bin
--out   / -o     : Output-Ordner  (repo-relativ oder absolut), Default: EWS/code/kontraste/laplace_per_image
--per-file-csv   : Dateiname der Ausgabedatei, Default: laplace_per_file.csv
--sigma          : σ für optionale Gauss-Glättung vor Laplace (float, Default: 1.0; 0 = aus)

# Beispiel
python laplace_per_image.py --input-img EWS/data/img/img_bin --out EWS/code/kontraste/laplace_per_image --sigma 1.0

# Hinweise
- Pipeline: (optional) Gaussian(I, σ) → Laplace(ksize=3) → var(L) / (var(I_smooth)+1e-12)
- Misst lokale Kanten/Feinstrukturen; höher = „hüppeligere“ (detailreichere) Bilder.
- Die 5-Bit-Maske ist **optional** und wird nur extrahiert, wenn im Dateinamen vorhanden.
"""

from pathlib import Path
import argparse, os, sys
import numpy as np
import pandas as pd
from skimage import io, color, filters

# --------------------------------------------------------------------------------------
# CLI / Pfade
# --------------------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Laplace pro Bild (ohne Gaze): normalisierte Laplace-Varianz")
    # Eingabe (repo-relativ ODER absolut)
    p.add_argument("--input-img", default=os.environ.get("EWS_IMG_DIR", "EWS/data/img/img_bin"),
                   help="Bild-Ordner (jpg/png; repo-relativ oder absolut).")
    # Output (repo-relativ ODER absolut)
    p.add_argument("--out", "-o", default=os.environ.get("EWS_OUT_DIR", "EWS/code/kontraste/laplace_per_image"),
                   help="Output-Ordner für CSV.")
    # Metrik-Parameter
    p.add_argument("--sigma", type=float, default=1.0,
                   help="Gauss-Glättung vor Laplace (σ). 0 = aus.")
    # Dateiname für per-file CSV
    p.add_argument("--per-file-csv", default="laplace_per_file.csv",
                   help="Dateiname für die per-File-CSV (relativ zu --out).")
    return p.parse_args()

ARGS = parse_args()

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parents[2] if len(SCRIPT_DIR.parents) >= 2 else SCRIPT_DIR

def R(pth: str, root: Path) -> Path:
    p = Path(pth)
    return p if p.is_absolute() else (root / p)

IMG_DIR = R(ARGS.input_img, REPO_ROOT)
OUT_DIR = R(ARGS.out, REPO_ROOT)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Bilder suchen ---
image_paths = sorted({
    p for ext in ("*.jpg","*.jpeg","*.png","*.bmp","*.tif","*.tiff")
    for p in IMG_DIR.rglob(ext)
})
if not image_paths:
    sys.exit(f"Keine Bilder gefunden in: {IMG_DIR}")

print(f"[Info] IMG_DIR : {IMG_DIR}  ({len(image_paths)} Bilder)")
print(f"[Info] OUT_DIR : {OUT_DIR}")

# --------------------------------------------------------------------------------------
# Bild laden (Graustufen [0,1]) & Laplace-Metrik
# --------------------------------------------------------------------------------------
def load_gray01(path: str) -> np.ndarray:
    img = io.imread(path)
    if img.ndim == 2:
        g = img.astype(np.float32)
        if g.max() > 1.0: g /= 255.0
        return g
    if img.ndim == 3:
        if img.shape[2] >= 3:
            img = img[..., :3]
        img = img.astype(np.float32)
        if img.max() > 1.0: img /= 255.0
        return color.rgb2gray(img).astype(np.float32)
    raise ValueError(f"Unsupported image shape: {img.shape}")

def laplacian_var_norm(gray01: np.ndarray, sigma: float = 1.0) -> float:
    """
    Normalisierte Laplace-Varianz:
      1) optional glätten (Gaussian σ)
      2) Laplace-Filter (ksize=3)
      3) var(L) / (var(I_smooth) + eps)
    """
    I = gray01
    if sigma > 0:
        I = filters.gaussian(I, sigma=sigma, preserve_range=True)
    L = filters.laplace(I, ksize=3)
    vL = float(np.var(L, ddof=0))
    vI = float(np.var(I, ddof=0))
    return float(vL / (vI + 1e-12))

# --- Loop & CSV ---
rows, errors = [], 0
for p in image_paths:
    try:
        g = load_gray01(p)
        val = laplacian_var_norm(g, sigma=max(0.0, ARGS.sigma))
      
        rows.append({
            "stem": p.stem,
            "lap_var_norm": val
        })
    except Exception as e:
        errors += 1
        print(f"[Warnung] Fehler bei {p}: {e}")

df = pd.DataFrame(rows).sort_values(["stem"])

out_csv = (OUT_DIR / ARGS.per_file_csv).resolve()
df.to_csv(out_csv, index=False)

print("\n[OK] CSV gespeichert:", out_csv)
print(f"[Info] Auswertbar: {len(df)} | Fehler: {errors}")
# Optional: kurzer Überblick
if not df.empty:
    print(df.head(5))

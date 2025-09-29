"""
# correlation_rms.py
# Zweck
Prüft, ob der **RMS-Kontrast** von Bildern mit **Fixations­metriken** aus Eye-Tracking
zusammenhängt (Pearson-Korrelation). Optional werden Ausreißer per 5–95 %-Quantil
begrenzt, pro Bild über alle Personen aggregiert und Scatterplots erzeugt.

# Eingaben
1) Bildwerte:
   - Entweder: per-Bild-CSV mit `stem`, `rms_contrast` (empfohlen: aus rms_per_image.py)

2) Fixationen (Parquet/CSV):
   - Dateien mit Spalten wie: `start_ms`, `end_ms`, `duration_ms`, `x`, `y`, `n_samples`
   - Mehrere Personen/Trials pro Bild sind erlaubt

# Matching / Keys
- Bilder und Fixationen werden über **stem** gematcht (z. B. `P01_IMG004_10100`).

# Ausgaben
- `<OUT>/correlation_rms.csv`:
  - `N` (Anzahl Bilder), `pearson_r`, `p_value`, Zielmetrik (z. B. `fix_count`, `fix_dur_total`)
- `<OUT>/scatter_fix_count.png`, `<OUT>/scatter_fix_dur_total.png`:
  - Scatterplots mit Regressionslinie; Achsen: x=RMS, y=Fixationskennzahl

# Kennzahlen (pro Bild, vor Korrelation)
- `fix_count`        : Anzahl Fixationen (nach 5–95 %-Filter)
- `fix_dur_total`    : Summe Fixations­dauern (ms) (nach 5–95 %-Filter)
- optional weitere (mean/median Dauer) je nach Skript-Einstellung


# Hinweise
- RMS misst globalen Helligkeitskontrast (frequenz-/ortsunabhängig).
- Pearson r≈1 → starker positiver Zusammenhang (mehr Kontrast bedeutet mehr/ längere Fixationen),
  r≈0 → kein linearer Zusammenhang, r<0 → negativer Zusammenhang.
"""

from pathlib import Path
import argparse, os, re, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
from itertools import islice

# ---------------- CLI / Pfade ----------------
def parse_args():
    p = argparse.ArgumentParser(description="Korrelation: RMS (Kontrast) vs. Fixationen (getrimmt)")
    p.add_argument(
    "--rms-csv",
    default=os.environ.get("EWS_RMS_PERFILE", "EWS/code/kontraste/rms_per_image/rms_per_file.csv"),
    help="Pfad zur RMS-CSV (repo-relativ oder absolut).")
    p.add_argument("--fix-dir",
                   default=os.environ.get("EWS_FIX_DIR", "EWS/code/preprocess/events/fixations"),
                   help="Ordner mit Fixations-Parquet (repo-relativ oder absolut)")
    p.add_argument("--out",
                   default=os.environ.get("EWS_OUT_DIR", "EWS/code/kontraste/contrast_fixation_corr"),
                   help="Output-Ordner")
    p.add_argument("--qlo", type=float, default=0.05, help="unteres Quantil fürs Trimmen (default 0.05)")
    p.add_argument("--qhi", type=float, default=0.95, help="oberes Quantil fürs Trimmen (default 0.95)")
    p.add_argument("--engine", default="pyarrow", choices=["pyarrow", "fastparquet"],
                   help="Parquet-Engine (default pyarrow)")
    p.add_argument("--spearman", action="store_true", help="zusätzlich Spearman berechnen")
    return p.parse_args()

ARGS = parse_args()
ENGINE = getattr(ARGS, "engine", "pyarrow")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parents[2] if len(SCRIPT_DIR.parents) >= 2 else SCRIPT_DIR

def R(pth: str, root: Path) -> Path:
    p = Path(pth)
    return p if p.is_absolute() else (root / p)

RMS_CSV = R(ARGS.rms_csv, REPO_ROOT).resolve()
FIX_DIR = R(ARGS.fix_dir, REPO_ROOT).resolve()
OUT_DIR = R(ARGS.out, REPO_ROOT).resolve()
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"[Info] RMS-CSV    : {RMS_CSV}")
print(f"[Info] Fixation DIR: {FIX_DIR}")
print(f"[Info] OUT DIR     : {OUT_DIR}")
print(f"[Info] Parquet Eng.: {ENGINE}")

# ---------------- Key-Normalisierung ----------------
BIN_MASK_RE       = re.compile(r"_[01]{5}(?![0-9])", re.IGNORECASE)
VIEWER_PREFIX_RE  = re.compile(r"^(?:proband\d+_|p\d+_)", re.IGNORECASE)

def canonical_key_from_name(name: str) -> str:
    base = name.lower()
    base = VIEWER_PREFIX_RE.sub("", base)     
    m = BIN_MASK_RE.search(base)
    if m:
        return base[:m.end()]                 
    return base                               

def canonical_key_from_path(path: Path) -> str:
    return canonical_key_from_name(path.stem)

# ---------------- Utils ----------------
def trimmed_mean(series: pd.Series, qlo=0.05, qhi=0.95) -> float:
    s = pd.Series(series, dtype=float).dropna().to_numpy()
    if s.size == 0:
        return np.nan
    lo, hi = np.quantile(s, [qlo, qhi])
    s_trim = s[(s >= lo) & (s <= hi)]
    if s_trim.size == 0:
        return np.nan
    return float(np.mean(s_trim))

def safe_corr(x, y, method="pearson"):
    x = pd.Series(x, dtype=float)
    y = pd.Series(y, dtype=float)
    mask = x.notna() & y.notna()
    x, y = x[mask], y[mask]
    if x.size < 3:
        return np.nan, np.nan, int(x.size)
    if method == "pearson":
        r, p = pearsonr(x, y)
    else:
        r, p = spearmanr(x, y)
    return float(r), float(p), int(x.size)

def scatter_plot(x, y, xlabel, ylabel, title, out_png):
    x = pd.Series(x, dtype=float)
    y = pd.Series(y, dtype=float)
    m = x.notna() & y.notna()
    x, y = x[m], y[m]
    if x.size < 3:
        return
    coeffs = np.polyfit(x, y, deg=1)
    xp = np.linspace(x.min(), x.max(), 100)
    yp = coeffs[0]*xp + coeffs[1]
    plt.figure(figsize=(7.5, 6))
    plt.scatter(x, y, alpha=0.7)
    plt.plot(xp, yp, lw=2)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png, dpi=180)
    plt.close()

# ---------------- 1) RMS-CSV laden ----------------
if not RMS_CSV.exists():
    sys.exit(f"RMS-CSV nicht gefunden: {RMS_CSV}")

df_rms = pd.read_csv(RMS_CSV)

# stem ermitteln
if "stem" not in df_rms.columns:
    # versuche aus einer Pfadspalte abzuleiten
    for cand in ["file_image", "file", "path"]:
        if cand in df_rms.columns:
            df_rms["stem"] = df_rms[cand].apply(lambda p: Path(str(p)).stem)
            break
    if "stem" not in df_rms.columns:
        sys.exit("RMS-CSV hat weder 'stem' noch eine Pfadspalte ('file_image'|'file'|'path').")

# RMS-Spalten-Kandidaten
RMS_COL_CANDIDATES = [
    "rms_contrast", "rms", "rms_luma", "rms_value", "rms_gray", "rms_intensity"
]
RMS_COL = next((c for c in RMS_COL_CANDIDATES if c in df_rms.columns), None)
if RMS_COL is None:
    sys.exit(f"Keine RMS-Spalte gefunden. Erwarte eine der: {RMS_COL_CANDIDATES}")

# --- nach dem Einlesen von df_rms und Setzen von RMS_COL & 'stem' ---

# Key-Normalisierung wie gehabt:
df_rms["key"] = df_rms["stem"].astype(str).apply(canonical_key_from_name)

# Falls 'label' fehlt: aus 5-Bit-Maske im stem ableiten (Reihenfolge: meme, ort, person, politik, text)
import re
MASK_RE = re.compile(r"([01]{5})(?![0-9])")
CATS = ["meme","ort","person","politik","text"]

def label_from_stem(stem: str) -> str:
    s = str(stem).lower()
    m = MASK_RE.search(s)
    if not m:
        return ""  # oder "unknown"
    mask = m.group(1)
    parts = [CATS[i] for i, bit in enumerate(mask) if bit == "1"]
    return "_".join(parts) if parts else ""  # oder "none"

if "label" not in df_rms.columns:
    df_rms["label"] = df_rms["stem"].apply(label_from_stem)

# Jetzt robust aggregieren: wenn 'label' existiert, nimm das erste je key; sonst leer lassen
if "label" in df_rms.columns:
    df_rms_img = (df_rms.groupby("key", as_index=False)
                        .agg(rms=(RMS_COL, "mean"),
                             label=("label", "first")))
else:
    df_rms_img = (df_rms.groupby("key", as_index=False)
                        .agg(rms=(RMS_COL, "mean")))
    df_rms_img["label"] = ""

print(f"[Info] RMS-Bilder (unique): {len(df_rms_img)}")



df_rms["key"] = df_rms["stem"].astype(str).apply(canonical_key_from_name)
df_rms_img = (df_rms.groupby("key", as_index=False)
                    .agg(rms=("{}".format(RMS_COL), "mean"),
                         label=("label", lambda s: s.iloc[0] if len(s)>0 else "")))
print(f"[Info] RMS-Bilder (unique): {len(df_rms_img)}")

# ---------------- 2) Fixations-Parquet lesen ----------------
parquets = list(FIX_DIR.rglob("*.parquet")) + list(FIX_DIR.rglob("*.PARQUET"))
if not parquets:
    print(f"[Warnung] Keine Parquet-Dateien in: {FIX_DIR}")

def read_fix_parquet(path: Path, engine: str) -> pd.DataFrame:
    try:
        return pd.read_parquet(path, engine=engine)
    except ImportError as e:
        raise SystemExit(
            f"Parquet-Engine '{engine}' fehlt: {e}. "
            f"Installiere z.B.: pip install {engine}"
        )

rows = []
for pq in parquets:
    key = canonical_key_from_path(pq)
    try:
        dfp = read_fix_parquet(pq, engine=ENGINE)
    except Exception as e:
        print(f"[Warnung] Kann Parquet nicht lesen: {pq.name} → {e}")
        continue

    if "duration_ms" not in dfp.columns:
        print(f"[Warnung] 'duration_ms' fehlt in {pq.name}; Spalten: {list(dfp.columns)[:10]}")
        continue

    n_fix  = int(dfp.shape[0])
    tot_ms = float(dfp["duration_ms"].sum())
    med_ms = float(dfp["duration_ms"].median()) if n_fix > 0 else np.nan

    rows.append({
        "key": key,
        "file": str(pq),
        "n_fixations": n_fix,
        "total_duration_ms": tot_ms,
        "median_duration_ms": med_ms
    })

df_view = pd.DataFrame(rows)
if df_view.empty:
    sys.exit("Keine verwertbaren Fixationsdaten gefunden (prüfe --fix-dir und Parquet-Spalten).")

# ---------------- 3) Pro Bild (über Betrachter) getrimmte Mittelwerte ----------------
agg_per_image = (df_view.groupby("key")
                 .agg(n_fix_mean_trim=("n_fixations", lambda s: trimmed_mean(s, ARGS.qlo, ARGS.qhi)),
                      tot_dur_mean_trim=("total_duration_ms", lambda s: trimmed_mean(s, ARGS.qlo, ARGS.qhi)),
                      med_dur_mean_trim=("median_duration_ms", lambda s: trimmed_mean(s, ARGS.qlo, ARGS.qhi)),
                      n_viewers=("n_fixations", "size"))
                 .reset_index())

print(f"[Info] Bilder mit Fixationsdaten (aggregiert): {len(agg_per_image)}")

# ---------------- Debug: Keys vergleichen (vor Merge) ----------------
rms_keys = set(df_rms_img["key"])
fix_keys = set(agg_per_image["key"])
inter    = rms_keys & fix_keys

print(f"[Debug] Keys RMS: {len(rms_keys)} | Fixations: {len(fix_keys)} | Schnittmenge: {len(inter)}")

# ---------------- 4) Merge RMS ⟷ Fixationsaggregate ----------------
df_merged = pd.merge(df_rms_img, agg_per_image, on="key", how="inner")
if df_merged.empty:
    sys.exit("Keine Schnittmenge zwischen RMS-Bildern und Fixations-Bildern")

# ---------------- 5) Korrelationen ----------------
targets = {
    "n_fix_mean_trim":   "getrimmtes Mittel der Fixationsanzahl",
    "tot_dur_mean_trim": "getrimmtes Mittel der Gesamtdauer (ms)",
    "med_dur_mean_trim": "getrimmtes Mittel der Median-Dauer (ms)",
}

lines = []
for col, desc in targets.items():
    rP, pP, nP = safe_corr(df_merged["rms"], df_merged[col], method="pearson")
    lines.append(f"Pearson  rms vs {col:<18} (n={nP:3d}): r = {rP: .4f}, p = {pP:.3g}  [{desc}]")
    if ARGS.spearman:
        rS, pS, nS = safe_corr(df_merged["rms"], df_merged[col], method="spearman")
        lines.append(f"Spearman rms vs {col:<18} (n={nS:3d}): ρ = {rS: .4f}, p = {pS:.3g}  [{desc}]")

print("\n".join(lines))

# ---------------- 6) Scatterplots ----------------
for col, desc in targets.items():
    rP, pP, nP = safe_corr(df_merged["rms"], df_merged[col], method="pearson")
    title = f"RMS vs {col}  (Pearson r={rP:.3f}, p={pP:.3g}, n={nP})"
    out_png = OUT_DIR / f"scatter_rms_vs_{col}.png"
    scatter_plot(df_merged["rms"], df_merged[col],
                 xlabel="RMS-Kontrast (σ=StdAbw Intensitäten, [0..1])",
                 ylabel=desc,
                 title=title,
                 out_png=out_png)

print(f"\nFertig. Ergebnisse in: {OUT_DIR}")

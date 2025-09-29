"""
# correlation_laplace.py
# Zweck
Prüft, ob die **Laplace-Metrik** (normalisierte Laplace-Varianz; Kanten/Detailkontrast)
von Bildern mit **Fixations­metriken** korreliert (Pearson-Korrelation).
Ausreißer können per 5–95 %-Quantil begrenzt werden, es wird pro Bild über Personen aggregiert,
und Scatterplots werden erzeugt.

# Eingaben
1) Bildwerte:
   - Entweder: per-Bild-CSV mit `stem`, `lap_var_norm` (aus laplace_per_image.py)

2) Fixationen (Parquet/CSV):
   - Dateien mit: `start_ms`, `end_ms`, `duration_ms`, `x`, `y`, `n_samples`

# Matching / Keys
- Join über **stem** (z. B. `P01_IMG004_10100`).

# Ausgaben
- `<OUT>/correlation_laplace.csv`:
  - `N`, `pearson_r`, `p_value`, Zielmetrik (z. B. `fix_count`, `fix_dur_total`)
- `<OUT>/scatter_fix_count.png`, `<OUT>/scatter_fix_dur_total.png`:
  - Scatterplots mit Regressionslinie; Achsen: x=Laplace, y=Fixationskennzahl


# Kennzahlen (pro Bild, vor Korrelation)
- `fix_count`        : Anzahl Fixationen (nach 5–95 %-Filter)
- `fix_dur_total`    : Summe Fixations­dauern (ms) (nach 5–95 %-Filter)
- optional weitere (mean/median Dauer)

# Hinweise
- Laplace betont lokale Kanten/Feinstrukturen; oft näher an „salienten“ Details.
- Interpretation von Pearson r wie bei RMS.
"""

from pathlib import Path
import argparse, os, re, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
from itertools import islice

# ---------------- CLI / Pfade (repo-relativ wie in deinen anderen Skripten) ----------------
def parse_args():
    p = argparse.ArgumentParser(description="Korrelation: Laplace (Kontrast) vs. Fixationen (getrimmt)")
    p.add_argument("--laplace-csv",
                   default=os.environ.get("EWS_LAP_PERFILE", "EWS/code/kontraste/laplace_per_image/laplace_per_file.csv"),
                   help="CSV mit Laplace pro Bild (repo-relativ oder absolut)")
    p.add_argument("--fix-dir",
                   default=os.environ.get("EWS_FIX_DIR", "EWS/code/preprocess/events/fixations"),
                   help="Ordner mit Fixations-Parquet (repo-relativ oder absolut)")
    p.add_argument("--out",
                   default=os.environ.get("EWS_OUT_DIR", "EWS/code/kontraste/contrast_fixation_corr"),
                   help="Output-Ordner")
    p.add_argument("--qlo", type=float, default=0.05, help="unteres Quantil fürs Trimmen (0.05)")
    p.add_argument("--qhi", type=float, default=0.95, help="oberes Quantil fürs Trimmen (0.95)")
    p.add_argument("--engine", default="pyarrow", choices=["pyarrow", "fastparquet"],
                   help="Parquet-Engine (default pyarrow)")
    p.add_argument("--spearman", action="store_true", help="zusätzlich Spearman ausgeben")
    return p.parse_args()

ARGS = parse_args()
ENGINE = getattr(ARGS, "engine", "pyarrow")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parents[2] if len(SCRIPT_DIR.parents) >= 2 else SCRIPT_DIR

def R(pth: str, root: Path) -> Path:
    p = Path(pth)
    return p if p.is_absolute() else (root / p)

LAPLACE_CSV = R(ARGS.laplace_csv, REPO_ROOT).resolve()
FIX_DIR     = R(ARGS.fix_dir, REPO_ROOT).resolve()
OUT_DIR     = R(ARGS.out, REPO_ROOT).resolve()
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"[Info] Laplace CSV : {LAPLACE_CSV}")
print(f"[Info] Fixation DIR: {FIX_DIR}")
print(f"[Info] OUT DIR     : {OUT_DIR}")
print(f"[Info] Parquet Eng.: {ENGINE}")

# ---------------- Key-Normalisierung ----------------
# ..._10100 (5 Bits) erkennen, Prefixe wie P09_ / Proband12_ entfernen
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

# ---------------- 1) Laplace laden ----------------
if not LAPLACE_CSV.exists():
    sys.exit(f"Laplace-CSV nicht gefunden: {LAPLACE_CSV}")

df_lap = pd.read_csv(LAPLACE_CSV)

# Robustheit: 'stem' ggf. aus 'file_image' ableiten
if "stem" not in df_lap.columns:
    if "file_image" in df_lap.columns:
        df_lap["stem"] = df_lap["file_image"].apply(lambda p: Path(str(p)).stem)
    else:
        sys.exit("Laplace-CSV hat weder 'stem' noch 'file_image' – bitte eine der Spalten bereitstellen.")
if "lap_var_norm" not in df_lap.columns:
    sys.exit("Laplace-CSV fehlt Spalte 'lap_var_norm'.")

df_lap["key"] = df_lap["stem"].astype(str).apply(canonical_key_from_name)
df_lap_img = (df_lap.groupby("key", as_index=False)
                    .agg(lap_var_norm=("lap_var_norm","mean"),
                         stem=("stem", lambda s: s.iloc[0] if len(s)>0 else "")))
print(f"[Info] Laplace-Bilder (unique): {len(df_lap_img)}")

# ---------------- 2) Fixations-Parquet lesen (strikt Parquet) ----------------
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
lap_keys = set(df_lap_img["key"])
fix_keys = set(agg_per_image["key"])
inter    = lap_keys & fix_keys

print(f"[Debug] Keys Laplace: {len(lap_keys)} | Fixations: {len(fix_keys)} | Schnittmenge: {len(inter)}")

# ---------------- 4) Merge Laplace ⟷ Fixationsaggregate ----------------
df_merged = pd.merge(df_lap_img, agg_per_image, on="key", how="inner")
if df_merged.empty:
    sys.exit("Keine Schnittmenge zwischen Laplace-Bildern und Fixations-Bildern")

# ---------------- 5) Korrelationen ----------------
targets = {
    "n_fix_mean_trim":   "getrimmtes Mittel der Fixationsanzahl",
    "tot_dur_mean_trim": "getrimmtes Mittel der Gesamtdauer (ms)",
    "med_dur_mean_trim": "getrimmtes Mittel der Median-Dauer (ms)",
}

lines = []
for col, desc in targets.items():
    rP, pP, nP = safe_corr(df_merged["lap_var_norm"], df_merged[col], method="pearson")
    lines.append(f"Pearson  lap_var_norm vs {col:<18} (n={nP:3d}): r = {rP: .4f}, p = {pP:.3g}  [{desc}]")
    if ARGS.spearman:
        rS, pS, nS = safe_corr(df_merged["lap_var_norm"], df_merged[col], method="spearman")
        lines.append(f"Spearman lap_var_norm vs {col:<18} (n={nS:3d}): ρ = {rS: .4f}, p = {pS:.3g}  [{desc}]")

print("\n".join(lines))

# ---------------- 6) Scatterplots ----------------
for col, desc in targets.items():
    rP, pP, nP = safe_corr(df_merged["lap_var_norm"], df_merged[col], method="pearson")
    title = f"Laplace vs {col}  (Pearson r={rP:.3f}, p={pP:.3g}, n={nP})"
    out_png = OUT_DIR / f"scatter_laplace_vs_{col}.png"
    scatter_plot(df_merged["lap_var_norm"], df_merged[col],
                 xlabel="Laplace-Varianz (normalisiert)",
                 ylabel=desc,
                 title=title,
                 out_png=out_png)

print(f"\nFertig. Ergebnisse in: {OUT_DIR}")
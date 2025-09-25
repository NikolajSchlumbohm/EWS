"""
# rms_per_category.py
# Zweck
Liest eine per-Bild-CSV mit **RMS-Kontrast** ein, rekonstruiert (optional) die 5-Bit-Kategorie
aus dem Dateinamen und erzeugt **kategorienweise Auswertungen** (Aggregat-CSV, Heatmaps,
optional Signifikanztests) für vier vordefinierte Vergleichs-Sets.

# Eingaben
- CSV: `rms_per_file.csv` mit mindestens:
  - `stem`          – Dateiname ohne Erweiterung (enthält am Ende die 5-Bit-Maske …_xxxxx)
  - `rms_contrast`  – RMS-Kontrast des Bildes in [0,1]
- 5-Bit-Maske (optional, aber empfohlen): Reihenfolge
  ["meme","ort","person","politik","text"], z. B. `_10100`

# Ausgaben (pro Set in Unterordnern)
- `<OUT>/<SET>/rms_per_file.csv`  – gefilterte Zeilen des Sets
- `<OUT>/<SET>/rms_agg.csv`       – Aggregation je Label (count, mean, median, std, min, max)
- `<OUT>/<SET>/heat_values_mean.png`  (bzw. `_median`) – Heatmap der Kennzahl je Kategorie
- `<OUT>/<SET>/heat_diff_mean.png`    (bzw. `_median`) – Heatmap der absoluten Differenzen
- `<OUT>/<SET>/significance_summary.txt` (optional) – Kruskal–Wallis-Test
- `<OUT>/<SET>/pairwise_mwu_rms.csv`    (optional) – Paarweise Mann–Whitney (+ BH-FDR, r_bc)

# Vergleichs-Sets (vordefiniert)
1) singletons: meme, ort, person, politik, text
2) text-pairs + singletons: meme, ort, person, text, meme_text, ort_text, politik_text, person_text
3) person-chain: person, person_text, person_politik, person_text_politik
4) text_politik_meme vs. text_politik_person

# CLI / Pfade
--rms-csv   : Pfad zur per-Bild-CSV (repo-relativ oder absolut),
              Default: EWS/code/kontraste/rms_per_image/rms_per_file.csv
--out, -o   : Output-Ordner (Default: EWS/code/kontraste/rms_per_category)
--agg-stat  : "mean" oder "median" (steuert Heatmaps/Titel)
--digits    : Rundung der Anzeige (Default: 4)
--do-stats  : Signifikanztests aktivieren

# Beispiel
python rms_per_category.py --rms-csv EWS/code/kontraste/rms_per_image/rms_per_file.csv \
                           --out EWS/code/kontraste/rms_per_category \
                           --agg-stat mean --do-stats

# Hinweise
- RMS misst globale Helligkeitskontraste (frequenz-/ortsunabhängig).
- Labels werden bei Bedarf aus der 5-Bit-Maske in `stem` rekonstruiert.
- Heatmap-Farben sind dezent (Blues, beschnittene Skala).
"""

from pathlib import Path
import argparse, os, re, itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import kruskal, mannwhitneyu

# ---------------- CLI / Pfade ----------------
def parse_args():
    p = argparse.ArgumentParser(description="RMS Sets/Plots aus CSV (ohne Neuberechnung)")
    p.add_argument("--rms-csv",
                   default=os.environ.get("EWS_RMS_PERFILE",
                                          "EWS/code/kontraste/rms_per_image/rms_per_file.csv"),
                   help="CSV mit 'stem' und 'rms_contrast' (repo-relativ oder absolut)")
    p.add_argument("--out","-o",
                   default=os.environ.get("EWS_OUT_DIR",
                                          "EWS/code/kontraste/rms_per_category"),
                   help="Output-Ordner")
    p.add_argument("--agg-stat", choices=["mean","median"], default="mean")
    p.add_argument("--digits", type=int, default=4)
    p.add_argument("--do-stats", action="store_true")
    return p.parse_args()

ARGS = parse_args()
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parents[2] if len(SCRIPT_DIR.parents) >= 2 else SCRIPT_DIR

def R(pth: str, root: Path) -> Path:
    p = Path(pth)
    return p if p.is_absolute() else (root / p)

RMS_CSV = R(ARGS.rms_csv, REPO_ROOT).resolve()
OUT_DIR = R(ARGS.out, REPO_ROOT).resolve()
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"[Info] RMS-CSV : {RMS_CSV}")
print(f"[Info] OUT_DIR : {OUT_DIR}")

# ---------------- Maske/Label aus stem ----------------
BIT_ORDER = ["meme", "ort", "person", "politik", "text"]  # 10000=meme … 00001=text
BIN_RE = re.compile(r"_(?P<mask>[01]{5})(?![0-9])")

def stem_to_label(stem: str):
    m = BIN_RE.search(str(stem).lower())
    if not m:
        return None, None
    mask = m.group("mask")
    parts = [BIT_ORDER[i] for i, b in enumerate(mask) if b == "1"]
    return mask, ("_".join(parts) if parts else "none")

def canon_label(comps):
    s = set(comps)
    return "_".join([c for c in BIT_ORDER if c in s]) if s else "none"

# ---------------- Plots (dezente Blautöne) ----------------
def _truncate_cmap(cmap, minval=0.35, maxval=0.95, n=256):
    return LinearSegmentedColormap.from_list(f"trunc_{cmap.name}", cmap(np.linspace(minval, maxval, n)))

def plot_value_heatmap(values: pd.Series, counts: pd.Series, title: str, out_png: str,
                       stat_name="mean", digits=4):
    s_vals = values.dropna()
    cats = list(s_vals.index)
    if not cats: return
    vals = s_vals.to_numpy(float)
    ns   = counts.reindex(cats).fillna(0).astype(int).to_numpy()
    cmap_soft = _truncate_cmap(cm.get_cmap("Blues"), 0.35, 0.95)
    vmin, vmax = float(np.min(vals)), float(np.max(vals))
    if vmax <= vmin: vmin -= 1e-6; vmax += 1e-6
    fig, ax = plt.subplots(figsize=(max(7, 1.0*len(cats)+3), 3.0))
    im = ax.imshow(vals.reshape(1,-1), aspect='auto', cmap=cmap_soft, vmin=vmin, vmax=vmax)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04); cb.set_label(f"RMS ({stat_name})")
    ax.set_yticks([0], [f"RMS ({stat_name})"]); ax.set_xticks(range(len(cats)), cats)
    ax.set_title(title)
    for j, v in enumerate(vals):
        ax.text(j, 0, f"{v:.{digits}f}\n(n={ns[j]})", ha="center", va="center", color="black")
    fig.tight_layout(); fig.savefig(out_png, dpi=200); plt.close(fig)

def plot_diff_heatmap(values: pd.Series, counts: pd.Series, title: str, out_png: str,
                      stat_name="mean", digits=4):
    s_vals = values.dropna()
    cats = list(s_vals.index)
    if len(cats) < 2: return
    vals = s_vals.to_numpy(float)
    ns   = counts.reindex(cats).fillna(0).astype(int).to_numpy()
    M = np.abs(vals.reshape(-1,1) - vals.reshape(1,-1))
    cmap_soft = _truncate_cmap(cm.get_cmap("Blues"), 0.25, 0.85)
    n = len(cats); fig, ax = plt.subplots(figsize=(max(7, min(18, 0.9*n + 4)), max(7, min(18, 0.9*n + 4))))
    im = ax.imshow(M, aspect='equal', cmap=cmap_soft)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).set_label(f"|Δ RMS ({stat_name})|")
    ax.set_xticks(range(n), cats); ax.set_yticks(range(n), cats)
    ax.set_title(title + f" (|Δ {stat_name}|)")
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{M[i,j]:.{digits}f}\n(n={ns[i]}/{ns[j]})", ha="center", va="center", color="black")
    fig.tight_layout(); fig.savefig(out_png, dpi=200); plt.close(fig)

def run_stats_subset(df_img: pd.DataFrame, labels: list[str], out_dir: Path, feature="rms_contrast"):
    present = [l for l in labels if l in set(df_img["label"])]
    if len(present) < 2: return
    samples = [df_img.loc[df_img["label"]==l, feature].dropna().to_numpy() for l in present]
    H, p_kw = kruskal(*samples)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "significance_summary.txt", "w", encoding="utf-8") as f:
        f.write(f"Kruskal–Wallis (RMS): H={H:.3f}, p={p_kw:.3g}\n")
        f.write("Kategorien: " + ", ".join(present) + "\n")
    pairs = list(itertools.combinations(range(len(present)), 2))
    raw_p, rbc, names = [], [], []
    for i,j in pairs:
        a, b = present[i], present[j]
        x = df_img.loc[df_img["label"]==a, feature].to_numpy()
        y = df_img.loc[df_img["label"]==b, feature].to_numpy()
        pval = mannwhitneyu(x, y, alternative="two-sided").pvalue
        raw_p.append(pval); names.append(f"{a} vs {b}")
        nx, ny = len(x), len(y)
        U_greater = mannwhitneyu(x, y, alternative="greater").statistic
        rbc.append(2*U_greater/(nx*ny) - 1)
    raw_p = np.array(raw_p, float)
    order = np.argsort(raw_p); m = len(raw_p); adj = np.empty_like(raw_p); prev = 1.0
    for k in range(m-1, -1, -1):
        rank = k+1; val = raw_p[order[k]] * m / rank; prev = min(prev, val); adj[order[k]] = min(prev, 1.0)
    pd.DataFrame({"pair": names, "p_raw": raw_p, "p_fdr": adj, "effect_rbc": rbc})\
      .sort_values("p_fdr").to_csv(out_dir / "pairwise_mwu_rms.csv", index=False)

# ---------------- CSV laden & Labels bilden ----------------
if not RMS_CSV.exists():
    raise SystemExit(f"RMS-CSV nicht gefunden: {RMS_CSV}")

df = pd.read_csv(RMS_CSV)
if not {"stem","rms_contrast"}.issubset(df.columns):
    raise SystemExit("Erwarte Spalten 'stem' und 'rms_contrast' in der RMS-CSV.")

masks, labels = [], []
for s in df["stem"].astype(str):
    mask, label = stem_to_label(s)
    masks.append(mask); labels.append(label)
df["mask"]  = masks
df["label"] = labels
df = df.dropna(subset=["mask","label"])
if df.empty:
    raise SystemExit("Keine gültigen 5-Bit-Masken in 'stem' gefunden.")

print(f"[Info] Datensätze: {len(df)} | Labels: {sorted(df['label'].unique())}")

# ---------------- Deine 4 Sets ----------------
GROUPS = {
    "01_singletons_meme_ort_person_politik_text": [
        canon_label(["meme"]), canon_label(["ort"]),
        canon_label(["person"]), canon_label(["politik"]),
        canon_label(["text"]),
    ],
    "02_text_pairs_and_singletons": [
        canon_label(["meme"]), canon_label(["ort"]),
        canon_label(["person"]), canon_label(["text"]),
        canon_label(["meme","text"]), canon_label(["ort","text"]),
        canon_label(["politik","text"]), canon_label(["person","text"]),
    ],
    "03_person_chain": [
        canon_label(["person"]),
        canon_label(["person","text"]),
        canon_label(["person","politik"]),
        canon_label(["person","text","politik"]),
    ],
    "04_text_politik_meme_vs_text_politik_person": [
        canon_label(["text","politik","meme"]),
        canon_label(["text","politik","person"]),
    ],
}

# ---------------- Render je Set ----------------
for group_name, wanted in GROUPS.items():
    present = [l for l in wanted if l in set(df["label"])]
    if not present:
        print(f"[Info] {group_name}: keine passenden Labels, skip."); continue
    sub = df[df["label"].isin(present)].copy()
    agg = (sub.groupby("label")["rms_contrast"]
             .agg(["count","mean","median","std","min","max"])
             .reindex(present))
    group_dir = OUT_DIR / group_name
    group_dir.mkdir(parents=True, exist_ok=True)
    sub.to_csv(group_dir / "rms_per_file.csv", index=False)
    agg.to_csv(group_dir / "rms_agg.csv")

    vals, ns = agg[ARGS.agg_stat], agg["count"]
    plot_value_heatmap(vals, ns, title=f"RMS ({ARGS.agg_stat})",
                       out_png=str(group_dir / f"heat_values_{ARGS.agg_stat}.png"),
                       stat_name=ARGS.agg_stat, digits=ARGS.digits)
    plot_diff_heatmap(vals, ns, title="Differenz",
                      out_png=str(group_dir / f"heat_diff_{ARGS.agg_stat}.png"),
                      stat_name=ARGS.agg_stat, digits=ARGS.digits)

    if ARGS.do_stats and len(present) >= 2:
        run_stats_subset(sub, present, group_dir, "rms_contrast")

print(f"\nFertig. Ergebnisse in: {OUT_DIR}")

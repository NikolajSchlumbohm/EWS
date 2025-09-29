from __future__ import annotations

import argparse
import os
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd


def _load_mask(masks_dir: str, image_id: str) -> np.ndarray:
    from PIL import Image
    path = os.path.join(masks_dir, f"{image_id}.png")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Mask not found for image_id={image_id} at {path}")
    m = Image.open(path).convert("L")
    arr = np.array(m)
    return (arr > 127).astype(bool)


def _load_fixations_for_trial(fixations_dir: str, trial_id: str) -> pd.DataFrame:
    base = os.path.join(fixations_dir, f"{trial_id}")
    if os.path.exists(base + ".parquet"):
        try:
            return pd.read_parquet(base + ".parquet")
        except Exception:
            pass
    return pd.read_csv(base + ".csv")



def _parse_params_bounds(params_path: Optional[str]) -> Dict[str, float]:
    bounds: Dict[str, float] = {}
    if not params_path:
        return bounds
    if not os.path.exists(params_path):
        return bounds
    keys = {"stimulus_x0_norm", "stimulus_x1_norm", "stimulus_y0_norm", "stimulus_y1_norm"}
    with open(params_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, raw_val = line.split(":", 1)
            key = key.strip()
            if key not in keys:
                continue
            val = raw_val.strip().strip('\"\'')
            try:
                bounds[key] = float(val)
            except ValueError:
                continue
    return bounds
def _xy_to_pixel(x: float,
                 y: float,
                 w: int,
                 h: int,
                 coords_space: str,
                 bounds: Tuple[float, float, float, float]) -> Tuple[int, int, bool]:
    x0, x1, y0, y1 = bounds
    if coords_space == "display":
        denom_x = max(1e-9, x1 - x0)
        denom_y = max(1e-9, y1 - y0)
        xf = (x - x0) / denom_x
        yf = (y - y0) / denom_y
    else:
        xf = x
        yf = y
    inside = (0.0 <= xf <= 1.0) and (0.0 <= yf <= 1.0)
    xf = min(max(xf, 0.0), 1.0)
    yf = min(max(yf, 0.0), 1.0)
    col = int(round(xf * (w - 1))) if w > 1 else 0
    row = int(round(yf * (h - 1))) if h > 1 else 0
    return row, col, inside


def run_analysis(trial_summary_path: str,
                 fixations_dir: str,
                 masks_dir: str,
                 out_dir: str,
                 coords_space: str = "stimulus",
                 stimulus_bounds: Tuple[float, float, float, float] = (0.0, 1.0, 0.0, 1.0)) -> None:
    os.makedirs(out_dir, exist_ok=True)
    df_trials = pd.read_csv(trial_summary_path)
    rows = []
    missing_masks = 0
    for _, r in df_trials.iterrows():
        trial_id = str(r.get("trial_id"))
        image_id = str(r.get("image_id"))
        participant_id = str(r.get("participant_id"))
        # Load mask
        try:
            mask = _load_mask(masks_dir, image_id)
        except Exception:
            missing_masks += 1
            continue
        h, w = mask.shape
        # Load fixations
        try:
            fx = _load_fixations_for_trial(fixations_dir, trial_id)
        except Exception:
            continue
        if fx.empty:
            continue
        n_total = len(fx)
        n_in = 0
        dur_in = 0.0
        dur_total = float(fx["duration_ms"].sum()) if "duration_ms" in fx else 0.0
        for _, fr in fx.iterrows():
            x = float(fr.get("x", np.nan))
            y = float(fr.get("y", np.nan))
            if not np.isfinite(x) or not np.isfinite(y):
                continue
            row, col, inside_bounds = _xy_to_pixel(x, y, w, h, coords_space, stimulus_bounds)
            inside = inside_bounds and bool(mask[row, col])
            if inside:
                n_in += 1
                if "duration_ms" in fx:
                    dur_in += float(fr["duration_ms"]) if np.isfinite(fr.get("duration_ms", np.nan)) else 0.0
        n_out = n_total - n_in
        prop_in = n_in / n_total if n_total > 0 else np.nan
        prop_dur_in = dur_in / dur_total if dur_total > 0 else np.nan
        rows.append({
            "trial_id": trial_id,
            "participant_id": participant_id,
            "image_id": image_id,
            "n_fix_total": n_total,
            "n_fix_in_mask": n_in,
            "n_fix_out_mask": n_out,
            "prop_fix_in_mask": prop_in,
            "sum_dur_ms_total": dur_total,
            "sum_dur_ms_in_mask": dur_in,
            "prop_dur_in_mask": prop_dur_in,
        })

    trial_stats = pd.DataFrame(rows)
    trial_stats_path = os.path.join(out_dir, "trial_mask_fixation_stats.csv")
    trial_stats.to_csv(trial_stats_path, index=False)

    # Aggregate per participant
    part_cols = ["participant_id"]
    agg = trial_stats.groupby(part_cols, dropna=False).agg(
        n_trials=("trial_id", "count"),
        mean_prop_fix_in_mask=("prop_fix_in_mask", "mean"),
        median_prop_fix_in_mask=("prop_fix_in_mask", "median"),
        mean_prop_dur_in_mask=("prop_dur_in_mask", "mean"),
        median_prop_dur_in_mask=("prop_dur_in_mask", "median"),
    ).reset_index()
    part_stats_path = os.path.join(out_dir, "participant_mask_fixation_summary.csv")
    agg.to_csv(part_stats_path, index=False)

    # Global summary and rough hypothesis check (proportion > 0.5)
    more_than_half = (trial_stats["prop_fix_in_mask"] > 0.5).sum()
    valid_trials = trial_stats["prop_fix_in_mask"].notna().sum()
    overall_mean = float(trial_stats["prop_fix_in_mask"].mean()) if valid_trials else float("nan")
    overall_median = float(trial_stats["prop_fix_in_mask"].median()) if valid_trials else float("nan")

    summary = pd.DataFrame([
        {
            "n_trials_with_masks": int(valid_trials),
            "n_trials_prop>0.5": int(more_than_half),
            "pct_trials_prop>0.5": float(more_than_half / valid_trials * 100.0) if valid_trials else float("nan"),
            "mean_prop_fix_in_mask": overall_mean,
            "median_prop_fix_in_mask": overall_median,
            "missing_masks_trials": int(missing_masks),
        }
    ])
    summary_path = os.path.join(out_dir, "global_summary.csv")
    summary.to_csv(summary_path, index=False)

    print(f"Saved trial stats to {trial_stats_path}")
    print(f"Saved participant summary to {part_stats_path}")
    print(f"Saved global summary to {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze fixations over person masks")
    parser.add_argument("--trial-summary", default="code/preprocess/summaries/trial_summary.csv")
    parser.add_argument("--fixations-dir", default="code/preprocess/events/fixations")
    parser.add_argument("--masks-dir", default="code/segmentation/masks")
    parser.add_argument("--out-dir", default="code/segmentation/results")
    parser.add_argument("--params", default=None, help="Optional params.yaml to read stimulus bounds")
    parser.add_argument("--coords-space", choices=["stimulus", "display"], default="stimulus",
                        help="Coordinate space of fixations; set to 'display' for raw display-normalized gaze")
    parser.add_argument("--stimulus-x0", type=float, default=None,
                        help="Left edge of stimulus in display-normalized coords")
    parser.add_argument("--stimulus-x1", type=float, default=None,
                        help="Right edge of stimulus in display-normalized coords")
    parser.add_argument("--stimulus-y0", type=float, default=None,
                        help="Top edge of stimulus in display-normalized coords")
    parser.add_argument("--stimulus-y1", type=float, default=None,
                        help="Bottom edge of stimulus in display-normalized coords")
    args = parser.parse_args()

    params_bounds = _parse_params_bounds(args.params)

    def _pick(cli_val, key, default):
        if cli_val is not None:
            return cli_val
        if key in params_bounds:
            return params_bounds[key]
        return default

    bounds = (
        float(_pick(args.stimulus_x0, "stimulus_x0_norm", 0.0)),
        float(_pick(args.stimulus_x1, "stimulus_x1_norm", 1.0)),
        float(_pick(args.stimulus_y0, "stimulus_y0_norm", 0.0)),
        float(_pick(args.stimulus_y1, "stimulus_y1_norm", 1.0)),
    )
    if bounds[1] <= bounds[0] or bounds[3] <= bounds[2]:
        print("Warning: stimulus bounds invalid; falling back to full display")
        bounds = (0.0, 1.0, 0.0, 1.0)

    run_analysis(trial_summary_path=args.trial_summary,
                 fixations_dir=args.fixations_dir,
                 masks_dir=args.masks_dir,
                 out_dir=args.out_dir,
                 coords_space=args.coords_space,
                 stimulus_bounds=bounds)


if __name__ == "__main__":
    main()

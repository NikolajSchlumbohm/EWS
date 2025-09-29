from __future__ import annotations

import argparse
import glob
import os
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from .models import get_person_segmenter
import pandas as pd


def _image_id_from_filename(path: str) -> str:
    """Extract image_id (e.g., IMG001) from filename like IMG001_10100.jpg"""
    name = os.path.splitext(os.path.basename(path))[0]
    return name.split("_")[0]


def _save_mask(mask: np.ndarray, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # Save as 0/255 PNG via PIL
    img = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    img.save(out_path)


def _save_overlay(img: np.ndarray, mask: np.ndarray, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure(figsize=(6, 4))
    plt.imshow(img)
    plt.imshow(np.ma.masked_where(~mask, mask), cmap="Reds", alpha=0.4)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def _resolve_images_from_trial_summary(images_dir: str, trial_summary_path: str) -> list[tuple[str, str]]:
    """Resolve (image_id, image_path) pairs from trial_summary and available files.

    Picks first match for pattern f"{image_id}_*.jpg"; falls back to f"{image_id}.jpg".
    """
    image_paths: list[tuple[str, str]] = []
    df = pd.read_csv(trial_summary_path)
    ids = [str(x) for x in df["image_id"].dropna().unique().tolist()]
    for img_id in ids:
        candidates = sorted(glob.glob(os.path.join(images_dir, f"{img_id}_*.jpg")))
        if not candidates:
            fallback = os.path.join(images_dir, f"{img_id}.jpg")
            if os.path.exists(fallback):
                candidates = [fallback]
        if candidates:
            image_paths.append((img_id, candidates[0]))
        else:
            print(f"Warning: no image found for image_id={img_id} under {images_dir}")
    return image_paths


def run_segmentation(images_dir: str,
                     out_dir: str,
                     overlay_dir: Optional[str] = None,
                     save_overlays: bool = False,
                     weights: Optional[str] = None,
                     trial_summary: Optional[str] = None) -> None:
    seg = get_person_segmenter(weights=weights)
    if trial_summary:
        targets = _resolve_images_from_trial_summary(images_dir, trial_summary)
        paths = [p for (_, p) in targets]
        ids = [img_id for (img_id, _) in targets]
    else:
        paths = sorted(glob.glob(os.path.join(images_dir, "*.jpg")))
        ids = [_image_id_from_filename(p) for p in paths]
    if not paths:
        print(f"No images resolved (images_dir={images_dir}, trial_summary={trial_summary})")
        return

    skipped = 0
    made = 0
    for img_id, p in zip(ids, paths):
        try:
            img = np.array(Image.open(p).convert("RGB"))
            mask = seg.segment(img)
            out_path = os.path.join(out_dir, f"{img_id}.png")
            _save_mask(mask, out_path)
            made += 1
            if save_overlays and overlay_dir:
                ov_path = os.path.join(overlay_dir, f"{img_id}.png")
                _save_overlay(img, mask, ov_path)
        except RuntimeError as re:
            # Likely due to missing ultralytics; skip segmentation for this run
            print(f"Skipping segmentation for {p}: {re}")
            skipped += 1
            break  # no point continuing if backend missing
        except Exception as e:
            print(f"Failed to segment {p}: {e}")
            skipped += 1
    print(f"Segmentation complete. Masks created: {made}. Skipped: {skipped}.")


def main():
    parser = argparse.ArgumentParser(description="Generate person masks for images")
    parser.add_argument("--images-dir", default="data/img/img_bin")
    parser.add_argument("--out-dir", default="code/segmentation/masks")
    parser.add_argument("--overlay-dir", default="code/segmentation/overlays")
    parser.add_argument("--save-overlays", action="store_true")
    parser.add_argument("--weights", default=None)
    args = parser.parse_args()
    run_segmentation(args.images_dir, args.out_dir, args.overlay_dir, args.save_overlays, args.weights)


if __name__ == "__main__":
    main()

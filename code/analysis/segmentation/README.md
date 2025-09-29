Segmentation Package

Layout
- `src/YOLOv8Segmenter/`: Python package for person segmentation and analysis
- `masks/`: generated binary person masks per image (`1`=person, `0`=background)
- `overlays/`: optional visual overlays of masks and fixation points
- `results/`: analysis CSVs comparing fixations inside vs. outside masks

Dependencies
- Base: `numpy`, `pandas`, `matplotlib`, `pyarrow` (already in repo requirements)
- Optional (for automatic person masks): `ultralytics` (YOLOv8-seg) with weights, e.g. `yolov8n-seg.pt`.
  - Install: `pip install ultralytics`
  - Weights: the default model will auto-download if online; or pass `--weights` with a local path.

Usage
- Windows PowerShell:
  - Generate masks only for images present in preprocess summary:
    - `$env:PYTHONPATH='code\segmentation\src'; python -m YOLOv8Segmenter.pipeline --images-dir data\img\img_bin --out-dir code\segmentation\masks --trial-summary code\preprocess\summaries\trial_summary.csv`
    - Add a local YOLOv8-seg weights path if offline: `--weights path\to\yolov8n-seg.pt`
    - Add overlays: `--save-overlays --overlay-dir code\segmentation\overlays`
  - Analyze fixations vs masks using preprocess outputs:
    - `$env:PYTHONPATH='code\segmentation\src'; python -m YOLOv8Segmenter.analysis --trial-summary code\preprocess\summaries\trial_summary.csv --fixations-dir code\preprocess\events\fixations --masks-dir code\segmentation\masks --out-dir code\segmentation\results`

- Linux/WSL:
  - `PYTHONPATH=code/segmentation/src python3 -m YOLOv8Segmenter.pipeline --images-dir data/img/img_bin --out-dir code/segmentation/masks --trial-summary code/preprocess/summaries/trial_summary.csv`
  - `PYTHONPATH=code/segmentation/src python3 -m YOLOv8Segmenter.analysis --trial-summary code/preprocess/summaries/trial_summary.csv --fixations-dir code/preprocess/events/fixations --masks-dir code/segmentation/masks --out-dir code/segmentation/results`

Notes
- If `ultralytics` is not installed or weights are unavailable, the pipeline will fall back to a dummy segmenter and skip mask generation (it will report which images were skipped). You can also place precomputed masks into `code/segmentation/masks/IMGXXX.png` to run the analysis independently of the model.
- Fixation coordinates are assumed normalized to `[0,1]` as produced by the preprocess pipeline; they are mapped to image pixels to test if they fall on a person mask.
- Using `--trial-summary` ensures masks are generated only for images present in your preprocess outputs (via `image_id`) and saved as `IMGxxx.png` keyed by `image_id`.


Coordinate Notes
- Fixation CSVs generated after 2025-09-17 use stimulus-normalized coordinates (after letterbox correction). If you need to analyze legacy fixations still in display coordinates, run `segmentation analyze` with `--coords-space display` and either pass `--stimulus-x0/x1/y0/y1` or point `--params` to the preprocess `params.yaml`.

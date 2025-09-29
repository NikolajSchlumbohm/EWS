import argparse
from . import get_person_segmenter
from .pipeline import run_segmentation
from .analysis import run_analysis, _parse_params_bounds


def main():
    parser = argparse.ArgumentParser(prog="segmentation", description="Person segmentation and fixation analysis")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_seg = sub.add_parser("segment", help="Generate person masks for images")
    p_seg.add_argument("--images-dir", default="data/img/img_bin", help="Directory with images (*.jpg)")
    p_seg.add_argument("--out-dir", default="code/segmentation/masks", help="Output directory for binary masks")
    p_seg.add_argument("--overlay-dir", default="code/segmentation/overlays", help="Output directory for overlays")
    p_seg.add_argument("--save-overlays", action="store_true", help="Save overlay images with masks")
    p_seg.add_argument("--weights", default=None, help="Path to YOLOv8-seg weights (e.g., yolov8n-seg.pt)")
    p_seg.add_argument("--trial-summary", default=None, help="If provided, only segment images present in this preprocess summary (uses image_id)")

    p_an = sub.add_parser("analyze", help="Analyze fixations vs person masks")
    p_an.add_argument("--trial-summary", default="code/preprocess/summaries/trial_summary.csv",
                      help="Path to trial_summary.csv from preprocess")
    p_an.add_argument("--fixations-dir", default="code/preprocess/events/fixations",
                      help="Directory containing per-trial fixations (*.parquet or *.csv)")
    p_an.add_argument("--masks-dir", default="code/segmentation/masks", help="Directory with person masks")
    p_an.add_argument("--out-dir", default="code/segmentation/results", help="Directory for analysis outputs")
    p_an.add_argument("--params", default=None, help="Optional params.yaml to read stimulus bounds")
    p_an.add_argument("--coords-space", choices=["stimulus", "display"], default="stimulus",
                      help="Coordinate space of fixations; set to 'display' for raw display-normalized gaze")
    p_an.add_argument("--stimulus-x0", type=float, default=None,
                      help="Left edge of stimulus in display-normalized coords")
    p_an.add_argument("--stimulus-x1", type=float, default=None,
                      help="Right edge of stimulus in display-normalized coords")
    p_an.add_argument("--stimulus-y0", type=float, default=None,
                      help="Top edge of stimulus in display-normalized coords")
    p_an.add_argument("--stimulus-y1", type=float, default=None,
                      help="Bottom edge of stimulus in display-normalized coords")

    args = parser.parse_args()

    if args.cmd == "segment":
        run_segmentation(images_dir=args.images_dir,
                         out_dir=args.out_dir,
                         overlay_dir=args.overlay_dir,
                         save_overlays=args.save_overlays,
                         weights=args.weights,
                         trial_summary=args.trial_summary)
    elif args.cmd == "analyze":
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

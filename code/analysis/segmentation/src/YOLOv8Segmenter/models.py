from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class PersonSegmenter:
    """Abstract interface for a person segmenter returning boolean masks.

    Methods
    -------
    segment(image: np.ndarray) -> np.ndarray
        Return HxW boolean mask where True indicates person pixels.
    """

    def segment(self, image: np.ndarray) -> np.ndarray:  # pragma: no cover - interface only
        raise NotImplementedError


class DummySegmenter(PersonSegmenter):
    def segment(self, image: np.ndarray) -> np.ndarray:
        # No segmentation available; return all-false mask
        h, w = image.shape[:2]
        return np.zeros((h, w), dtype=bool)


class YOLOv8Segmenter(PersonSegmenter):
    def __init__(self, weights: Optional[str] = None):
        try:
            from ultralytics import YOLO  # type: ignore
        except Exception as e:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "ultralytics not available. Install with `pip install ultralytics` or provide precomputed masks."
            ) from e
        self._YOLO = YOLO
        self._model = YOLO(weights or "yolov8n-seg.pt")
        # Prefer GPU if available
        try:  # pragma: no cover - environment dependent
            import torch
            self._device = 0 if torch.cuda.is_available() else "cpu"
        except Exception:
            self._device = "cpu"

    def segment(self, image: np.ndarray) -> np.ndarray:
        # Run model; combine all instance masks where cls==0 (person in COCO)
        # Explicitly set device to prefer CUDA when available
        results = self._model.predict(image, verbose=False, device=self._device)
        if not results:
            h, w = image.shape[:2]
            return np.zeros((h, w), dtype=bool)
        r = results[0]
        # If no masks present, return zeros
        if getattr(r, "masks", None) is None or getattr(r, "boxes", None) is None:
            h, w = image.shape[:2]
            return np.zeros((h, w), dtype=bool)

        cls = r.boxes.cls.cpu().numpy().astype(int)
        masks = r.masks.data.cpu().numpy()  # (N, H, W) float 0..1
        person_mask = np.zeros(masks.shape[1:], dtype=bool)
        for i, c in enumerate(cls):
            if c == 0:  # person class in COCO
                person_mask |= masks[i] > 0.5
        return person_mask


def get_person_segmenter(weights: Optional[str] = None) -> PersonSegmenter:
    """Return a person segmenter.

    Prefers YOLOv8-seg if available; otherwise returns a dummy that segments nothing.
    """
    try:
        return YOLOv8Segmenter(weights=weights)
    except Exception:
        return DummySegmenter()

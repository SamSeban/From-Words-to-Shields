
"""Detector: faces → mask stream (placeholder interface only)."""

from tool_api import PrivacyTool
from registry import register

class DetectFaces(PrivacyTool):
    name = "detect_faces"

    def apply(self, video_path: str, detector: str = "haar", **kwargs):
        """Return a path to the produced mask stream.
        Later: run actual detection and write per-frame mask(s).
        Example returns:
            { "mask_stream_path": "data/results/street_faces_mask.npz" }
        """
        return {"mask_stream_path": "data/results/REPLACE_WITH_REAL_MASK_PATH"}

    def verify(self, **kwargs):
        """Optionally verify masks exist/align with video length."""
        return {"ok": True}

TOOL = DetectFaces()
register(TOOL)

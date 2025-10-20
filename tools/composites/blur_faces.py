
"""Composite: detect faces then blur (placeholder flow only)."""

from tool_api import PrivacyTool
from registry import get, register

class BlurFaces(PrivacyTool):
    name = "blur_faces"

    def apply(self, video_path: str, kernel: int = 31, detector: str = "haar", **kwargs):
        """Convenience wrapper:
        1) detect_faces(video_path, detector) → mask_stream_path
        2) blur(video_path, mask_stream_path, kernel) → video_path (blurred)
        NOTE: The actual calling order will be implemented in your runner;
              this stub only communicates intended flow.
        """
        # Placeholder output only
        return {"video_path": "data/results/REPLACE_WITH_BLURRED_VIDEO_PATH"}

    def verify(self, **kwargs):
        return {"ok": True}

TOOL = BlurFaces()
register(TOOL)

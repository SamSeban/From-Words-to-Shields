"""
Detector: identifies sensitive keywords in audio → outputs segments file.
"""

from tool_api import PrivacyTool
from registry import register


class DetectKeywords(PrivacyTool):
    name = "detect_keywords"

    def apply(self, audio_path, keywords, **kwargs):
        # TODO: Run ASR and find keyword timestamps.
        return {"segments_path": "data/results/REPLACE_WITH_SEGMENTS_PATH"}

    def verify(self, **kwargs):
        # TODO: Verify segments file is valid.
        return {"ok": True}


TOOL = DetectKeywords()
register(TOOL)

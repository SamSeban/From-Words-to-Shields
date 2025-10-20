"""
Transform: mutes audio segments based on provided timestamps.
"""

from tool_api import PrivacyTool
from registry import register


class MuteSegments(PrivacyTool):
    name = "mute_segments"

    def apply(self, audio_path, segments_path, mode="silence", **kwargs):
        # TODO: Apply muting (silence/beep) for each segment.
        return {"audio_path": "data/results/REPLACE_WITH_MUTED_AUDIO_PATH"}

    def verify(self, **kwargs):
        # TODO: Verify that keywords are no longer audible/textual.
        return {"ok": True}


TOOL = MuteSegments()
register(TOOL)
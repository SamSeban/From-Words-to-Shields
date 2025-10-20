
"""Composite: detect sensitive keywords then mute corresponding audio segments.

Intended flow (implemented later by your runner or explicit calls):
  1) detect_keywords(audio_path, keywords, asr='whisper') -> segments_path
  2) mute_segments(audio_path, segments_path, mode='silence'|'beep') -> audio_out_path

This composite provides a convenient single-step tool name: 'mute_keywords'.
"""

from tool_api import PrivacyTool
from registry import get, register

class MuteKeywords(PrivacyTool):
    name = "mute_keywords"

    def apply(self, audio_path: str, keywords, asr: str = "whisper", mode: str = "silence", **kwargs):
        """Convenience wrapper:
        - Detect keyword time ranges using ASR.
        - Mute those ranges in the audio using the chosen mode.
        NOTE: Actual calling order is handled by your pipeline/runner; this is a placeholder.
        Returns:
            { "audio_path": "data/results/REPLACE_WITH_MUTED_AUDIO_PATH" }
        """
        # Call detect_keywords to find keyword timestamps
        detect = get("detect_keywords")
        mute   = get("mute_segments")
        segs   = detect.apply(audio_path=audio_path, keywords=keywords, asr=asr)
        out    = mute.apply(audio_path=audio_path, segments_path=segs["segments_path"], mode=mode)
        return out

    def verify(self, **kwargs):
        """Optionally re-run ASR and confirm keywords are no longer audible/textual."""
        return {"ok": True}

TOOL = MuteKeywords()
register(TOOL)

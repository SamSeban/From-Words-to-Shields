"""Composite: detect faces then blur (placeholder flow only)."""

from tool_api import PrivacyTool
from registry import register

class BlurFaces(PrivacyTool):
    name = "blur_faces"

    def apply(self, video_path: str):
        """Convenience wrapper:
        1) detect_faces(video_path, detector) → mask_stream_path
        2) blur(video_path, mask_stream_path, kernel) → video_path (blurred)
        NOTE: The actual calling order will be implemented in your runner;
              this stub only communicates intended flow.
        """
        from registry import get  # Import here, not at top
        
        detect = get('detect_faces')
        blur = get('blur')
        
        if detect is None:
            raise RuntimeError("detect_faces tool not found in registry")
        if blur is None:
            raise RuntimeError("blur tool not found in registry")
        
        segs   = detect.apply(video_path=video_path)
        check_segs = detect.verify(segs)
        if check_segs['pass']:
            out= blur.apply(data_detection=segs)
            check_blur = blur.verify(result_blur = out, detection_file = segs)
            if check_blur['blur_verified']:
                return {"video_path":out['output_video_path']}
            else:
                print("blur didnt pass")
                return
        else:
            print("detection didnt pass")
            return

    def verify(self, **kwargs):
        return {"ok": True}

TOOL = BlurFaces()
register(TOOL)

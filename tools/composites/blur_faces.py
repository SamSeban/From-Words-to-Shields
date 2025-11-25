"""Composite: detect faces then blur (placeholder flow only)."""

from tool_api import PrivacyTool
from registry import register

class BlurFaces(PrivacyTool):
    name = "blur_faces"

    def apply(self, video_path: str, live=False):
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
        
        if live:
            # streaming frame by frame
            segs = detect.apply(video_path=video_path, live=True, visualize = False)
            out = blur.apply(data_detection=segs, video_path = video_path, live= True)
            for blurred_frame in out:
                yield blurred_frame

        else: 
            segs = detect.apply(video_path=video_path, visualize = True, live=False)
            # consume generator for detection
            for _ in segs:
                    pass
            out = blur.apply(data_detection=None, video_path=video_path, live=False)
            # Consume generator for blur
            for _ in out:
                    pass
   
    def verify(self, **kwargs):
        return {"ok": True}

TOOL = BlurFaces()
register(TOOL)

if __name__ == "__main__":
    video_path='/home/daniel/Downloads/2.mp4'

    for iteration in TOOL.apply(video_path=video_path, live=True):
        pass
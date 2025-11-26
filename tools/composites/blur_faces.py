"""Composite: detect faces then blur (placeholder flow only)."""

from tool_api import PrivacyTool
from registry import register

class BlurFaces(PrivacyTool):
    name = "blur_faces"

    # this function is used to consume a generator and keep the last yield. Both in DetectFaces and in Blur, in the non-live mode,
    # the last yield returns the full info about the video, so we need to keep it
    def consume_generator(self, gen):
        last = None
        for last in gen:
            pass
        return last

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
            result_detect = self.consume_generator(detect.apply(video_path=video_path, visualize = True, live=False))
            check_detection = detect.verify(result_detect)
            if check_detection['pass']:
                out = None
                result_blur = self.consume_generator(blur.apply(data_detection=result_detect, video_path=video_path, live=False))
                check_blurring = blur.verify(result_blur, result_detect)

   
    def verify(self, **kwargs):
        return {"ok": True}

TOOL = BlurFaces()
register(TOOL)

if __name__ == "__main__":
    video_path='/home/daniel/Downloads/4.mp4'

    for iteration in TOOL.apply(video_path=video_path, live=False):
        pass
"""
Live censoring: blur faces and mute keywords in real-time with synchronized playback.

Both audio and video are delayed by the same amount so that:
- Audio keywords can be detected and beeped before playback
- Video faces can be detected and blurred before display
- Audio and video remain in sync
"""

import time
import threading
import cv2

# Import PLAYBACK_DELAY from the mute_keywords_live module
from tools.composites.mute_keywords_live import PLAYBACK_DELAY, TOOL as mute_tool

# Import registry to get the tools
from registry import get


class LiveCensor:
    """Runs face blurring and keyword muting simultaneously with synchronized delay."""
    
    def __init__(self, playback_delay: float = PLAYBACK_DELAY):
        self.playback_delay = playback_delay
        self.video_queue = []  # (timestamp, frame) pairs
        self.running = False
        
    def _mute_keywords_worker(self, keywords: list):
        """Worker thread that runs keyword detection and muting."""
        try:
            mute_tool.detect_keyword(keywords)
        except Exception as e:
            print(f"Error in keyword muting: {e}")
    
    def run(self, keywords: list, video_path: str = "camera"):
        """
        Start live censoring with both face blurring and keyword muting.
        
        Args:
            keywords: List of keywords to mute (beep out)
            video_path: Path to video file or "camera" for webcam
        """
        self.running = True
        
        print(f"Starting live censoring with {self.playback_delay}s delay...")
        print(f"Keywords to mute: {keywords}")
        print("Press 'q' in the video window or Ctrl+C to stop.")
        
        # Start the keyword muting in a background thread (audio via pygame works in threads)
        mute_thread = threading.Thread(
            target=self._mute_keywords_worker, 
            args=(keywords,), 
            daemon=True
        )
        mute_thread.start()
        
        # Get the tools for face detection and blurring
        detect_faces = get('detect_faces')
        blur = get('blur')
        
        if detect_faces is None:
            print("ERROR: detect_faces tool not found in registry")
            return
        if blur is None:
            print("ERROR: blur tool not found in registry")
            return
        
        # Save original imshow and suppress it for blur tool
        original_imshow = cv2.imshow
        
        try:
            # Run face detection in live mode - this yields (frame, detection) tuples
            detection_gen = detect_faces.apply(video_path=video_path, live=True, visualize=False)
            
            # Pass a dummy path for blur (it only uses it for output filename)
            blur_gen = blur.apply(data_detection=detection_gen, video_path="live_censored.avi", live=True)
            
            # Suppress imshow during the entire blur iteration
            cv2.imshow = lambda *args, **kwargs: None
            
            for blurred_frame in blur_gen:
                # Add frame to queue with current timestamp
                self.video_queue.append((time.time(), blurred_frame))
                
                # Temporarily restore imshow just for our delayed display
                cv2.imshow = original_imshow
                
                # Display frames that are old enough (past the delay threshold)
                while self.video_queue:
                    timestamp, queued_frame = self.video_queue[0]
                    age = time.time() - timestamp
                    
                    if age >= self.playback_delay:
                        # Frame is old enough, display it
                        cv2.imshow("Live Censored (Delayed)", queued_frame)
                        self.video_queue.pop(0)
                        
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            self.running = False
                            cv2.imshow = original_imshow  # Restore before returning
                            return
                    else:
                        # Not old enough yet, wait a bit
                        break
                
                # Suppress again for next blur iteration
                cv2.imshow = lambda *args, **kwargs: None
                            
        except KeyboardInterrupt:
            print("\n\nStopping live censoring...")
        finally:
            # Restore imshow
            cv2.imshow = original_imshow
            
            self.running = False
            # Drain remaining frames
            print("Draining video buffer...")
            while self.video_queue:
                timestamp, queued_frame = self.video_queue.pop(0)
                cv2.imshow("Live Censored (Delayed)", queued_frame)
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            
            time.sleep(0.3)
            cv2.destroyAllWindows()


if __name__ == "__main__":
    censor = LiveCensor()
    for iteration in censor.run(keywords=["shit", "fuck"], video_path="camera"):
        pass
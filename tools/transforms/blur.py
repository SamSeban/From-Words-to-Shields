
"""Transform: blur regions where mask==1 (placeholder interface only)."""

from tool_api import PrivacyTool
from registry import register
import cv2
import os
import time

class Blur(PrivacyTool):
    name = "blur"


    def apply(self, data_detection,  kernel: int = 51):
        """Load the data from the detection. The value of the kernel determines how blurry the image is (high num, 
        high blur), however high blur means more computation necessary. Take data from the detection face section
        """
        if not data_detection:
            raise NameError("not found detections")
        # take just the face boxes from data detection
        detections = {d["frame"]: d["boxes"] for d in data_detection["detections"]}
        video_path = data_detection["video_path"]


        # start video reader/writer
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Could not open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Output path
        os.makedirs("data/results", exist_ok=True)
        filename = os.path.basename(video_path)
        output_path = os.path.join("data/results", f"blurred_{filename}")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        scale = 2 # take 2 times more for safety. This parameter can be tuned

        frame_idx = 0
        

        start_time = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            boxes = detections.get(frame_idx, None)
            if boxes is None:
                print(f"Boxes is empty, frame Index: {frame_idx}")

            # Apply blur for each face box
            if boxes:
                for box in boxes:
                    x, y, w, h = map(float, box)
                    cx, cy = x + w / 2.0, y + h / 2.0
                    new_w, new_h = w * scale, h * scale
                    # clamp to image
                    x1 = int(max(cx - new_w / 2.0, 0))
                    y1 = int(max(cy - new_h / 2.0, 0))
                    x2 = int(min(cx + new_w / 2.0, frame.shape[1]))
                    y2 = int(min(cy + new_h / 2.0, frame.shape[0]))
                    roi = frame[y1:y2, x1:x2]
                    if roi.size > 0:
                        # ensure kernel odd and <= ROI size
        
                        blurred = cv2.GaussianBlur(roi, (kernel, kernel), 0)
                        frame[y1:y2, x1:x2] = blurred

            cv2.imshow("Face Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            out.write(frame)
            frame_idx += 1
        
        cap.release()
        out.release()
        end_time = time.time()
        total_time = end_time - start_time
        fps_proc = frame_idx / total_time

        results = {
            "input_video_path": video_path,
            "output_video_path": output_path,
            'detections_file': 'output_face_detection.json',
            'verification_detection_file': 'result_verification.json',
            "summary": {"fps_processed": round(fps_proc, 3), "ratio_speed_output_input": round(fps_proc/fps, 3)}
        }

        return results


    def verify(self, result_blur, detection_file):
        """Optionally check blur intensity in masked regions.
        Use Laplacian to check for sharpness in the blurred region."""
        
        detections = detection_file['detections']
        video_path = result_blur['output_video_path']
        cap = cv2.VideoCapture(video_path)
    
        if not cap.isOpened():
            raise IOError(f"Could not open video: {video_path}")

        blur_ratios = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # find detection by frame_idx
            current_detection = next((d for d in detections if d["frame"] == frame_idx), None)
            if current_detection is None:
                frame_idx += 1
                continue

            boxes = current_detection.get("boxes", [])
            for (x, y, w, h) in boxes:
                x, y, w, h = map(int, [x, y, w, h])
                roi = frame[y:y+h, x:x+w]
                if roi.size == 0:
                    continue
                # Laplacian variance measures sharpness
                lap_var = cv2.Laplacian(roi, cv2.CV_64F).var()
                blur_ratios.append(lap_var)
            
            frame_idx += 1

        cap.release()
        avg_blur = sum(blur_ratios) / len(blur_ratios) if blur_ratios else 0
        blur_threshold = 50 #this param can be tuned. Here's a breakdwon: 
        # >200: Sharp, unblurred face, blur is weak. 100-200: slight blur, insufficient
        # 50-100: moderate blur, not really good for privacy. <50: strong blur, recommended for privacy
        # <20 very strong blur, excellent
        strong_blur = bool(avg_blur < blur_threshold) 

        report = {
            "video_path": video_path,
            "avg_laplacian_variance": float(avg_blur),  # cast to float to avoid np.float64 issue
            "blur_verified": strong_blur,
            "frames_checked": frame_idx,
        }

        return report

    
TOOL = Blur()
register(TOOL)

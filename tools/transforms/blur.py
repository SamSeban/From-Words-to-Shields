"""Transform: blur regions where mask==1 (placeholder interface only)."""

from tool_api import PrivacyTool
from registry import register
import cv2
import os
import time
import json

class Blur(PrivacyTool):
    name = "blur"


    def apply(self, data_detection, video_path, kernel: int = 81, live : bool = False):
        """
        If live==False: expect data_detection to be the dict produced by detector.apply(...)
        If live==True: expect data_detection to be a generator yielding (frame, detection) tuples
                        where detection is {"frame": idx, "boxes": [...], ...}
        For now using only the live version, consider changing the structure or removing it
        """
        os.makedirs("data/results", exist_ok=True)
        filename_base, filename_ext = os.path.splitext(os.path.basename(video_path))
        output_path = os.path.join("data/results", f"blurred_{filename_base}.avi")
        
        # live mode: generator of (frame, detection) ---
        if live:
            gen = data_detection

            first_item = next(gen, None)
            if first_item is None:
                cv2.destroyAllWindows()
                return {"error": "no frames received from the detector"}
            if isinstance(first_item, tuple) and len(first_item) == 2:
                initial_frame, initial_detection = first_item
            else:
                raise RuntimeError("Streaming blur expects (frame, detection) tuples from detector.")
            height, width = initial_frame.shape[:2]
            # placeholder, will need a more robus way to find the fps of the video
            fps = 30
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            # If someone mistakenly passed the finished dict with a 'detections' list:
            if isinstance(data_detection, dict) and "detections" in data_detection:
                raise RuntimeError("In live mode expected a generator, got a dict.")
                     

            # Consume generator and output blurred frames as another generator
            for item in gen:
                
                # support both (frame, detection) and (detection,) forms
                if isinstance(item, tuple) and len(item) == 2:
                    frame, detection = item
                else:
                    # If detector yields only detection dicts (not recommended),
                    # we cannot find the corresponding frame without reopening the video;
                    # raise a clear error so devs will change the detector yield accordingly.
                    raise RuntimeError()

                boxes = detection.get("boxes", [])
                # apply blur onto the frame (in-place)
                if boxes:
                    scale = 2  # same as offline code, tuneable
                    for box in boxes:
                        x, y, w, h = map(float, box)
                        cx, cy = x + w / 2.0, y + h / 2.0
                        new_w, new_h = w * scale, h * scale
                        x1 = int(max(cx - new_w / 2.0, 0))
                        y1 = int(max(cy - new_h / 2.0, 0))
                        x2 = int(min(cx + new_w / 2.0, frame.shape[1]))
                        y2 = int(min(cy + new_h / 2.0, frame.shape[0]))
                        roi = frame[y1:y2, x1:x2]
                        if roi.size > 0:
                            k = kernel if kernel % 2 == 1 else kernel + 1
                            # clamp kernel not larger than roi
                            kx = min(k, roi.shape[0] if roi.shape[0] % 2 == 1 else roi.shape[0] - 1)
                            ky = min(k, roi.shape[1] if roi.shape[1] % 2 == 1 else roi.shape[1] - 1)
                            kx = max(1, kx); ky = max(1, ky)
                            # Use a square kernel (must be odd)
                            kk = kx if kx == ky else max(kx, ky)
                            if kk % 2 == 0:
                                kk += 1
                            blurred = cv2.GaussianBlur(roi, (kk, kk), 0)
                            frame[y1:y2, x1:x2] = blurred

                # show or yield the blurred frame
                cv2.imshow("Face Detection (live blurred)", frame)
                out.write(frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    # If user wants to stop streaming early, break
                    break
                # yield blurred frame to caller
                yield frame
            # streaming ended; cleanup windows
            out.release()
            cv2.destroyAllWindows()
            
        
        # Offline mode
        else: 
            with open("result_detection.json", "r") as f:
                data_detection = json.load(f)
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

                cv2.imshow("Face Blurring", frame)
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

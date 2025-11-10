from tool_api import PrivacyTool
import cv2
import numpy as np
import os
import time
from registry import register



class DetectFaces(PrivacyTool):
    name = "detect_faces"

    def make_kalman_filter(x, y, w, h):
        """Create a 12D Kalman filter for position, velocity, and acceleration."""

        # Now the kalman filter predicts takes also position. However people's movement is usually
        # without acceleration -> can change it to 8D (remove acceleration row) to make it (maybe) faster
        # and (maybe) more robust (less stuff to predict, less mistakes). From a first quick check, the results are
        # very similar
        kf = cv2.KalmanFilter(12, 4)
        dt = 1.0
        kf.transitionMatrix = np.eye(12, dtype=np.float32)
        # set coeffs. the transition matrix is [x, y, w, h; vx, vy, vw, vh; ax, ay, aw, ah;]
        for i in range(4):
            kf.transitionMatrix[i, i + 4] = dt
            kf.transitionMatrix[i, i + 8] = 0.5 * dt * dt
            kf.transitionMatrix[i + 4, i + 8] = dt

        kf.measurementMatrix = np.zeros((4, 12), np.float32)
        for i in range(4):
            kf.measurementMatrix[i][i] = 1.0

        # Process and measurement noise. These values can be tuned, and higher values make the filter
        # more aggressive
        kf.processNoiseCov = np.eye(12, dtype=np.float32)
        kf.processNoiseCov[:4, :4] *= 0.01
        kf.processNoiseCov[4:8, 4:8] *= 0.5
        kf.processNoiseCov[8:12, 8:12] *= 2.0
        kf.measurementNoiseCov = np.eye(4, dtype=np.float32) * 0.1

        kf.statePost = np.array(
            [[x], [y], [w], [h], [0], [0], [0], [0], [0], [0], [0], [0]], np.float32
        )
        kf.errorCovPost = np.eye(12, dtype=np.float32)
        return kf


    def apply(self, video_path: str, visualize=False, detect_interval=3, scale=None):
        """Detect faces using YuNet + Tracker + Kalman hybrid system.
        The logic is: according to the detect interval, if the detectors didnt fail too many times in a row
        (in that case we believe there is nobody), and if the kalman filter is old -> detect. Otherwise, use a tracker
         and if the tracker fails, use a kalman filter. Handle grayscale videos using clahe. Log stats to decide 
         detection quality"""        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video, check path: {video_path}")

        # Check first frame to get info about the video
        ret, first_frame = cap.read()
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        # the way to check if the video is grayscale is if there are 2 channels (not rgb), or rgb but
        # values are close to each other
        is_grayscale = len(first_frame.shape) < 3 or (
            np.allclose(first_frame[..., 0], first_frame[..., 1])
            and np.allclose(first_frame[..., 1], first_frame[..., 2])
        )
        
        video_description = ['grayscale', 'dude ringing bell', 'delivery guy', 'kid 1', 'dude at entrance',
                              'dude walking towards camera', 'kid 2', 'delivery 2 black lady', 'kid 3'] # just to match video and number in testing

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_num = int(video_path[23]) - 1
        # print(f"[INFO] {os.path.basename(video_path)} | {width}x{height} | {fps:.2f} FPS | {frame_count} frames | description: {video_description[video_num]}")

        # Load YuNet detector
        model_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../models/face_detection_yunet_2023mar.onnx")
        )
        if not os.path.exists(model_path):
            raise FileNotFoundError("YuNet model missing in models/ folder.")

        # These parameters can be tuned.
        detector = cv2.FaceDetectorYN.create(
            model=model_path,
            config='',
            input_size=(320, 320),
            score_threshold=0.5,
            nms_threshold=0.3,
            top_k=5000,
            backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
            target_id=cv2.dnn.DNN_TARGET_CPU,
        )

        #  Config parameters
        max_size = 780
        kalman_predict_limit = 6  # fallback for tracker fail, max number of consecutive kalman prediction. Can be tuned
        frame_idx = 0

        trackers = None
        # kf_filters, kf_ages = [], []
        kf_filters = []
        #  Metrics
        total_detects, frames_with_faces, frames_no_faces = 0, 0, 0
        no_face_in_frame, tracker_recoveries = 0, 0
        kalman_only_frames = 0
        missed_detections = 0
        kalman_detections = 0

        start_time = time.time()
        predict_counter = 0

        detections = []
        consecutive_non_detections = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # scale down the size of the video, taking 780 as max size and keeping ratio
            orig_h, orig_w = frame.shape[:2]
            scale = min(max_size / max(orig_h, orig_w), 1.0)
            resized_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)

            # decide when to detect: 1) if the frame is in the detect interval, 2) if the detector fails less than twice again 
            # and there is no tracker on, 3) if the kalman filter is "old" and it's prediction is not very trustworthy anymore
            do_detect = (
                (frame_idx % detect_interval == 0)
                or (consecutive_non_detections < 2 and trackers is None) # Add a controlled check
                or predict_counter >= kalman_predict_limit
            )

            if do_detect:
                # check if its grayscale just when detecting, not for each frame. Use clahe to improve contrast
                if is_grayscale:                    
                    gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
                    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(6, 6))
                    clahe_frame = clahe.apply(gray)
                    gaussian = cv2.GaussianBlur(clahe_frame, (0, 0), 2.0)
                    clahe_frame = cv2.addWeighted(clahe_frame, 1.8, gaussian, -0.8, 0)
                    resized_frame = cv2.cvtColor(np.clip(clahe_frame, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
                
                total_detects += 1
                kalman_detections = 0

                detector.setInputSize((resized_frame.shape[1], resized_frame.shape[0]))
                _, faces = detector.detect(resized_frame)

                
                face_boxes = []


                if faces is not None and len(faces) > 0:
                    consecutive_non_detections = 0
                    predict_counter = 0
                    # when find face, add tracker, and create a new empty kalman filter 
                    trackers = cv2.legacy.MultiTracker_create()
                    new_kf_filters = []
                    for face in faces:
                        x, y, w, h = face[:4]
                        x, y, w, h = [int(v / scale) for v in (x, y, w, h)]
                        box = (x, y, w, h)
                        face_boxes.append(box)
                        # link tracker and kalman to the face
                        trackers.add(cv2.legacy.TrackerKCF_create(), frame, box)
                        new_kf_filters.append(DetectFaces.make_kalman_filter(float(x), float(y), float(w), float(h)))
                    kf_filters = new_kf_filters
                    detection = {"frame": frame_idx, "boxes": face_boxes, "source": "detector"}
                else:
                    consecutive_non_detections += 1
                    no_face_in_frame += 1
                    missed_detections += 1
                    face_boxes = []

            else:
                # TRACKING PHASE
                if trackers is not None:
                    success, tracked_boxes = trackers.update(frame)
                else:
                    success, tracked_boxes = False, []

                if success:
                    # use tracker, set the kalman detections to 0
                    kalman_detections = 0
                    face_boxes = []
                    for i, tb in enumerate(tracked_boxes):
                        x_meas, y_meas, w_meas, h_meas = tb
                        if i < len(kf_filters): # if less tracked boxes than kalman filter, use kalman filter
                            kf = kf_filters[i]
                            kf.predict()
                            meas = np.array([[x_meas], [y_meas], [w_meas], [h_meas]], np.float32)
                            est = kf.correct(meas)
                            x, y, w, h = est[0, 0], est[1, 0], est[2, 0], est[3, 0]
                            face_boxes.append((int(x), int(y), int(w), int(h)))
                            
                        else: # otherwise just use the tracker
                            face_boxes.append((int(x_meas), int(y_meas), int(w_meas), int(h_meas)))
                        if len(face_boxes) > 0: # record data
                            detection  = {"frame": frame_idx, "boxes": face_boxes, "source": "tracker"}
                    tracker_recoveries += 1

                elif consecutive_non_detections < 3:
                    #  TRACKER FAILED → use Kalman predictions temporarily
                    
                    kalman_detections += 1
                    # predict_mode = True
                    predict_counter += 1
                    # print(f"Frame {frame_idx}: Tracker Failed. KF filters count: {len(kf_filters)}. Predict Counter: {predict_counter}, consecutive non detections: {consecutive_non_detections}")
                    kalman_only_frames += 1
                    face_boxes = []
                    for i, kf in enumerate(kf_filters):
                        pred = kf.predict()
                        x, y, w, h = pred[0, 0], pred[1, 0], pred[2, 0], pred[3, 0]
                        face_boxes.append((int(x), int(y), int(w), int(h)))
                        
                    if len(face_boxes) > 0:
                        detection = {"frame": frame_idx, "boxes": face_boxes, "source": "kalman", "outcome": "success"}
                    else:
        
                        detection = {"frame": frame_idx, "boxes": face_boxes, "source": "kalman", "outcome": "failed"}
            # --- Stats
            
            if len(face_boxes) > 0:
                frames_with_faces += 1
            else:
                frames_no_faces += 1
            # place rectangle on the video
            if visualize:
                vis = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
                for (x, y, w, h) in face_boxes:
                    xs, ys, ws, hs = [int(v * scale) for v in (x, y, w, h)]
                    cv2.rectangle(vis, (xs, ys), (xs + ws, ys + hs), (0, 0, 255), 2)
                
                cv2.imshow("Face Detection", vis)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            if len(face_boxes) == 0:
                detection = {"frame": frame_idx, "boxes": face_boxes, "outcome": "failed", "source": "failed"}
            detections.append(detection)  

            frame_idx += 1

        cap.release()
        cv2.destroyAllWindows()
        total_time = time.time() - start_time
        fps_proc = frame_idx / total_time

        # --- Accuracy metrics
        missed_ratio = missed_detections / total_detects if total_detects > 0 else 0
        detection_accuracy = (1 - missed_ratio) * 100 if total_detects > 0 else 0

        # print("\n========== PERFORMANCE SUMMARY ==========")
        # print(f"Frames processed:    {frame_idx}")
        # print(f"Detections run:      {total_detects}")
        # print(f"Frames with faces:   {frames_with_faces} ({(frames_with_faces / frame_idx * 100):.2f}%)")
        # print(f"Frames no faces:     {frames_no_faces} ({(frames_no_faces / frame_idx * 100):.2f}%)")
        # print(f"Tracker recoveries:  {tracker_recoveries}")
        # print(f"Kalman-only frames:  {kalman_only_frames} ({(kalman_only_frames/frame_idx * 100):.2f}%)")
        # print(f"Missed detections:   {missed_detections}")
        # print(f"Detection accuracy:  {detection_accuracy:.2f}%")
        # print(f"Effective FPS:       {fps_proc:.2f}")
        # print(f"Ratio processing rate over video fps: {round(fps_proc/fps, 3)}")
        # print("=========================================\n")

        results = { "video_path": video_path,
            "processed_frames": frame_idx, 
                   "detections": detections,
                   "stats": {
                       "avg_fps": round(fps_proc, 2),
                       "miss_ratio": missed_ratio,
                       "detection_accuracy": round(detection_accuracy, 3),
                       'fps_video': fps,
                   }}
    

        return results
    
    #-------------------------------------------------------------------------------------------------------------- 
    
    
    def verify(self, data):
        """Optionally verify masks exist/align with video length. The main issue are the small gaps, while for the long 
        gaps the assumption is that the subject is left.
        This possibly needs changing in the future, since with the kalman filters small gaps problems exist but 
        they are considerably less than when this was implemented"""

        
        
        num_faces_prev = 0
        gap_size = 0
        gaps = []
        total_frames = len(data['detections'])
        missing_frames = 0
        in_gap = False

        for index, detection in enumerate(data['detections']):
            num_faces_new = len(detection['boxes'])

            # A face count drop → start or continue a gap
            if num_faces_new < num_faces_prev:
                gap_size += 1
                missing_frames += (num_faces_prev - num_faces_new)
                in_gap = True

            # Still in a gap (no recovery yet)
            elif in_gap and num_faces_new <= num_faces_prev:
                gap_size += 1

            # Face count recovered or stable (end of gap)
            elif in_gap and num_faces_new >= num_faces_prev:
                gaps.append({'starting_frame': index - gap_size, 'gap_size': gap_size})
                gap_size = 0
                in_gap = False

            # Update for next iteration
            num_faces_prev = num_faces_new

        # Edge case: video ends mid-gap
        if in_gap:
            gaps.append({'starting_frame': total_frames - gap_size, 'gap_size': gap_size})
                
        miss_ratio = missing_frames / total_frames if total_frames > 0 else 0
        fps_video = data['stats']['fps_video']
        

        short_gaps = []
        short_gap_duration = fps_video * 0.5 # take 0.5 as the max duration of a short gap
        total_short_gap_time = 0
        successful_frames = total_frames - missing_frames
        
        for gap in gaps:
            if gap['gap_size'] < short_gap_duration:
                short_gaps.append(gap)
                total_short_gap_time += gap['gap_size']
        shortgap2success = total_short_gap_time / successful_frames 

        # pass in 2 cases
        # 1) there detection is good for at least 90%
        # 2) there are just short gaps in the detections (not more than 10%)
        decide_pass = (miss_ratio < 0.1 ) or (shortgap2success < 0.1)
        summary = {
            'video_path': data['video_path'], 
            'total_frames': total_frames,
            'missing_frames': missing_frames,
            'miss_ratio': round(miss_ratio, 3),
            "num_gaps": len(gaps),
            "fps_video": fps_video,
            'ratio_short_gaps_to_success': round(shortgap2success,3),
            "short_gaps_count": len(short_gaps),
            "total_short_gap_time": total_short_gap_time
            
        }

        results = {"gaps": gaps, "summary": summary, 'pass': decide_pass}

        return results


TOOL = DetectFaces()
register(TOOL)

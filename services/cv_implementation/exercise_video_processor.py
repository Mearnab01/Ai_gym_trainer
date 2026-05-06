import os
import cv2
import av
import numpy as np
import mediapipe as mp
import threading

from streamlit_webrtc import VideoProcessorBase
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from detectors.squat import SquatDetector
from detectors.pushup import PushUpDetector
from detectors.biceps_curl import BicepsCurlDetector
from detectors.shoulder_press import ShoulderPressDetector
from detectors.lunges import LungesDetector

from services.config.workout_config import SEGMENT_CONNECTIONS, SEGMENT_COLORS
from services.cv_implementation.frame_processor import AngleSmoother

class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_metrics = None
        self._exercise_type = "Squats"
        
        self._smoother = AngleSmoother()
        
        model_path = os.path.join(os.getcwd(), "ml_models", "pose_landmarker_full.task")
        base_option = python.BaseOptions(model_asset_path=model_path)
        
        options = vision.PoseLandmarkerOptions(
            base_options = base_option,
            running_mode = vision.RunningMode.VIDEO,
            min_pose_detection_confidence=0.7,
            min_pose_presence_confidence=0.7,
            min_tracking_confidence=0.7,
            output_segmentation_masks=False
        )
        
        self._landmarker = vision.PoseLandmarker.create_from_options(options)
        
        self._detectors = {
            "Squats": SquatDetector(),
            "Push-ups": PushUpDetector(),
            "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
            "Shoulder Press": ShoulderPressDetector(),
            "Lunges": LungesDetector(),
        }
        
        self._frame_timestamps_ms = 0
        
    def set_latest_metrics(self, metrics):
        with self._lock:
            self._latest_metrics = metrics.copy()
            
    def get_latest_metrics(self):
        with self._lock:
            return None if self._latest_metrics is None else self._latest_metrics.copy()
        
    def set_exercise(self, exercise_type):
        with self._lock:
            if exercise_type != self._exercise_type:
                self._smoother.reset()
                
            self._exercise_type = exercise_type
            
    def get_exercise(self):
        with self._lock:
            return self._exercise_type
        
    # ── Drawing helpers ───────────────────────────────────────────────────────
    def _draw_skeleton(self, img, landmarks):
        h, w = img.shape[:2]
 
        # Draw each body segment in its own colour
        for segment, connections in SEGMENT_CONNECTIONS.items():
            color = SEGMENT_COLORS[segment]
            thickness = 2 if segment == "face" else 3
            for s, e in connections:
                p1, p2 = landmarks[s], landmarks[e]
                vis_thresh = 0.5 if segment == "face" else 0.65
                if p1.visibility > vis_thresh and p2.visibility > vis_thresh:
                    cv2.line(img,
                             (int(p1.x * w), int(p1.y * h)),
                             (int(p2.x * w), int(p2.y * h)),
                             color, thickness, cv2.LINE_AA)
 
        # Joint dots — white with a subtle coloured ring for key joints
        key_joints = {11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28}
        for i, lm in enumerate(landmarks):
            if lm.visibility > 0.65:
                cx, cy = int(lm.x * w), int(lm.y * h)
                if i in key_joints:
                    cv2.circle(img, (cx, cy), 6, (74, 222, 128), 1, cv2.LINE_AA)
                    cv2.circle(img, (cx, cy), 3, (255, 255, 255), -1, cv2.LINE_AA)
                else:
                    cv2.circle(img, (cx, cy), 3, (200, 200, 200), -1, cv2.LINE_AA)
                    
    def _draw_no_pose(self, img):
        cv2.putText(img, "NO POSE DETECTED", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (74, 222, 128), 2, cv2.LINE_AA)
        cv2.putText(img, "PLEASE FACE THE CAMERA", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (74, 222, 128), 2, cv2.LINE_AA)
        
    def _draw_overlays(self, img, metrics, ex_type):
        if ex_type == "Squats":
            self._draw_squats_overlays(img, metrics)
        elif ex_type == "Push-ups":
            self._draw_pushup_overlays(img, metrics)
        elif ex_type == "Biceps Curls (Dumbbell)":
            self._draw_curl_overlays(img, metrics)
        elif ex_type == "Shoulder Press":
            self._draw_press_overlays(img, metrics)
        elif ex_type == "Lunges":
            self._draw_lunge_overlays(img, metrics)
            
    _ACCENT = (74, 222, 128)

    def _draw_squats_overlays(self, img, metrics):
        h, _ = img.shape[:2]
        cv2.putText(img, f"DEPTH: {metrics.get('depth_status', 'N/A')}",
                (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, self._ACCENT, 2)

    def _draw_pushup_overlays(self, img, metrics):
        h, _ = img.shape[:2]
        cv2.putText(img, f"BODY: {metrics.get('body_alignment', 'N/A')} | HIP: {metrics.get('hip_status', 'N/A')}",
                (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, self._ACCENT, 2)

    def _draw_curl_overlays(self, img, metrics):
        h, _ = img.shape[:2]
        cv2.putText(img, f"SWING: {metrics.get('swing_status', 'N/A')}",
                (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, self._ACCENT, 2)

    def _draw_press_overlays(self, img, metrics):
        h, _ = img.shape[:2]
        cv2.putText(img, f"EXT: {metrics.get('extension_status', 'N/A')} | BACK: {metrics.get('back_arch_status', 'N/A')}",
                (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, self._ACCENT, 2)

    def _draw_lunge_overlays(self, img, metrics):
        h, _ = img.shape[:2]
        cv2.putText(img, f"BALANCE: {metrics.get('balance_status', 'N/A')}",
                (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, self._ACCENT, 2)
        
    def recv(self, frame):
        image = np.asarray(
            cv2.flip(frame.to_ndarray(format="bgr24"), 1),
            dtype=np.uint8
        )
        
        mp_image = mp.Image(
            image_format = mp.ImageFormat.SRGB,
            data = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        )
        
        self._frame_timestamps_ms += 30
        result = self._landmarker.detect_for_video(mp_image, self._frame_timestamps_ms)
        
        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]
            
            self._draw_skeleton(image, landmarks)
            
            ex_type = self.get_exercise()
            detector = self._detectors.get(ex_type)
            
            if detector:
                raw_metrics = detector.process(landmarks)
                metrics = self._smoother.smooth(raw_metrics)
                
                metrics["pose_detected"] = True
                
                self._draw_overlays(image, metrics, ex_type)
                self.set_latest_metrics(metrics)
                
        else:
            self._draw_no_pose(image)
            
            with self._lock:
                if self._latest_metrics is not None:
                    self._latest_metrics["pose_detected"] = False
                    
                else:
                    self._latest_metrics = {"pose_detected": False}
                        
        return av.VideoFrame.from_ndarray(image, format="bgr24")
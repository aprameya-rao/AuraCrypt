import os
import sys

# Standard polite requests (which MediaPipe is ignoring)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '2'
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import cv2
import mediapipe as mp
import numpy as np

# ==========================================
# THE NUCLEAR OPTION: C++ STDERR GAG
# ==========================================
class SuppressStderr:
    """
    Context manager that temporarily points the OS-level standard error
    to /dev/null, physically preventing C++ from printing to the terminal.
    """
    def __enter__(self):
        self.null_fd = os.open(os.devnull, os.O_RDWR)
        # Save the current stderr (file descriptor 2)
        self.save_fd = os.dup(2)
        # Point stderr to /dev/null
        os.dup2(self.null_fd, 2)

    def __exit__(self, *_):
        # Restore stderr back to normal so Python errors still show up
        os.dup2(self.save_fd, 2)
        os.close(self.null_fd)
        os.close(self.save_fd)
# ==========================================


class KineticBiometricService:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.target_frames = 32    

    def process_video(self, video_path: str) -> np.ndarray:
        
        # 🚨 Wrap the MediaPipe initialization and processing in our gag!
        with SuppressStderr():
            with self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            ) as hands_tracker:
                raw_frames = self._extract_frames(video_path)
                raw_landmarks = self._extract_landmarks(raw_frames, hands_tracker)
        
        # The math processing is safe, it doesn't print C++ logs
        spatially_normalized = self._normalize_spatial(raw_landmarks)
        final_matrix = self._normalize_temporal(spatially_normalized)
        
        return final_matrix

    def _extract_frames(self, video_path: str) -> list:
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            frames.append(image)
            
        cap.release()
        return frames

    def _extract_landmarks(self, frames: list, hands_tracker) -> list:
        video_landmarks = []
        for frame in frames:
            results = hands_tracker.process(frame)
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                frame_data = [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]
                video_landmarks.append(frame_data)
        return video_landmarks
    
    def _normalize_spatial(self, raw_landmarks: list) -> np.ndarray:
        if not raw_landmarks:
            raise ValueError("No hand landmarks were detected in the video.")
        matrix = np.array(raw_landmarks) 
        wrist_coords = matrix[:, 0:1, :] 
        spatially_normalized = matrix - wrist_coords 
        return spatially_normalized

    def _normalize_temporal(self, spatial_matrix: np.ndarray) -> np.ndarray:
        original_frames = spatial_matrix.shape[0]
        num_landmarks = spatial_matrix.shape[1]
        num_coords = spatial_matrix.shape[2] 

        if original_frames == self.target_frames:
            return spatial_matrix.flatten()

        original_time = np.linspace(0, 1, original_frames)
        target_time = np.linspace(0, 1, self.target_frames)
        temporal_matrix = np.zeros((self.target_frames, num_landmarks, num_coords))

        for landmark in range(num_landmarks):
            for coord in range(num_coords):
                curve = spatial_matrix[:, landmark, coord]
                resampled_curve = np.interp(target_time, original_time, curve)
                temporal_matrix[:, landmark, coord] = resampled_curve

        final_1d_matrix = temporal_matrix.flatten()
        return final_1d_matrix
    

kinetic_service = KineticBiometricService()
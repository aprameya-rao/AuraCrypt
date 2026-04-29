import cv2
import mediapipe as mp
import numpy as np

class KineticBiometricService:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.target_frames = 32    

    def process_video(self, video_path: str) -> np.ndarray:
        # THE FIX: Move the Hands tracker initialization INSIDE the process loop
        # Use a 'with' block so it is safely destroyed from memory after the video
        with self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as hands_tracker:
            raw_frames = self._extract_frames(video_path)
            
            # Pass the isolated tracker to the extraction function
            raw_landmarks = self._extract_landmarks(raw_frames, hands_tracker)
        
        spatially_normalized = self._normalize_spatial(raw_landmarks)
        final_matrix = self._normalize_temporal(spatially_normalized)
        
        return final_matrix

    def _extract_frames(self, video_path: str) -> list:
        """Reads video using OpenCV and returns a list of frames."""
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
            # MediaPipe requires RGB images, OpenCV reads in BGR
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
        """
        Converts raw coordinates to be relative to the wrist (Landmark 0).
        Input: list of shape (Frames, 21, 3)
        Output: np.ndarray of shape (Frames, 21, 3)
        """
        if not raw_landmarks:
            raise ValueError("No hand landmarks were detected in the video.")

        # Convert Python list to a 3D NumPy array for fast matrix operations
        # Shape: (F, 21, 3) where F is the number of frames
        matrix = np.array(raw_landmarks) 

        # Extract the wrist coordinates for all frames. 
        # Shape becomes (F, 1, 3) so it can broadcast against the 21 landmarks.
        wrist_coords = matrix[:, 0:1, :] 

        # Vectorized subtraction: Subtract wrist (X,Y,Z) from all 21 landmarks
        spatially_normalized = matrix - wrist_coords 
        
        return spatially_normalized

    def _normalize_temporal(self, spatial_matrix: np.ndarray) -> np.ndarray:
        """
        Interpolates the spatial matrix to exactly 32 frames and flattens it.
        Input: np.ndarray of shape (Frames, 21, 3)
        Output: 1D np.ndarray of shape (2016,) -> (32 * 21 * 3)
        """
        original_frames = spatial_matrix.shape[0]
        num_landmarks = spatial_matrix.shape[1]
        num_coords = spatial_matrix.shape[2] # 3 (X, Y, Z)

        if original_frames == self.target_frames:
            # If by sheer luck it's exactly 32 frames, just flatten and return
            return spatial_matrix.flatten()

        # Create the original "time axis" and the target "time axis"
        original_time = np.linspace(0, 1, original_frames)
        target_time = np.linspace(0, 1, self.target_frames)

        # Create an empty matrix to hold the perfectly sized 32-frame data
        # Shape: (32, 21, 3)
        temporal_matrix = np.zeros((self.target_frames, num_landmarks, num_coords))

        # We must interpolate each X, Y, and Z coordinate for each landmark independently
        for landmark in range(num_landmarks):
            for coord in range(num_coords):
                # Extract the 1D time-series curve for this specific coordinate
                curve = spatial_matrix[:, landmark, coord]
                
                # Interpolate to stretch or shrink the curve to 32 points
                resampled_curve = np.interp(target_time, original_time, curve)
                
                # Place the normalized curve into our new matrix
                temporal_matrix[:, landmark, coord] = resampled_curve

        # Flatten the 3D matrix (32, 21, 3) into a strictly sized 1D array (2016,)
        # This 1D array is the final Biometric Matrix (B) ready for Cryptography.
        final_1d_matrix = temporal_matrix.flatten()
        
        return final_1d_matrix
    

kinetic_service = KineticBiometricService()
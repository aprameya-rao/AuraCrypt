import librosa
import numpy as np
import tempfile
import os

class AudioProcessor:
    def __init__(self, sample_rate=22050, n_mfcc=20, target_duration=2.0):
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.target_duration = target_duration
        self.target_samples = int(self.target_duration * self.sample_rate)

    async def extract_binary_features(self, audio_bytes: bytes) -> np.ndarray:
        """
        Processes raw audio bytes through a stabilization pipeline, extracts 
        vocal tract features (MFCCs), and binarizes them for cryptography.
        """
        # 1. Temporarily write bytes to disk to bypass the soundfile BytesIO bug
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name

        try:
            # Load audio from the physical file path instead of memory
            y, sr = librosa.load(tmp_file_path, sr=self.sample_rate)
        finally:
            # Crucial: Always clean up the physical file right after loading it
            # We use a try/finally block so it deletes even if librosa crashes
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

        # 2. Silence Trimming 
        y_trimmed, _ = librosa.effects.trim(y, top_db=20)

        # 3. Amplitude Normalization 
        y_normalized = librosa.util.normalize(y_trimmed)

        # 4. Enforce Exact Duration 
        if len(y_normalized) < self.target_samples:
            y_fixed = librosa.util.fix_length(y_normalized, size=self.target_samples)
        else:
            y_fixed = y_normalized[:self.target_samples]

        # 5. Extract MFCCs (The Audio Matrix)
        mfccs = librosa.feature.mfcc(y=y_fixed, sr=sr, n_mfcc=self.n_mfcc)

        # 6. CMVN (Cepstral Mean and Variance Normalization)
        mfccs_normalized = (mfccs - np.mean(mfccs, axis=1, keepdims=True)) / (np.std(mfccs, axis=1, keepdims=True) + 1e-8)

        # 7. Binarization (The Cryptographic Conversion)
        median_val = np.median(mfccs_normalized)
        binary_matrix = (mfccs_normalized > median_val).astype(np.uint8)

        return binary_matrix.flatten()

audio_service = AudioProcessor()
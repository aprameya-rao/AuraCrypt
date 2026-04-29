import numpy as np
import tempfile
import os
import torch
from speechbrain.inference.speaker import EncoderClassifier

class DeepAudioProcessor:
    def __init__(self):
        # This downloads a highly accurate, pre-trained speaker verification 
        # model locally to your machine on the first run.
        self.classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb"
        )

    def extract_binary_features(self, audio_bytes: bytes) -> np.ndarray:
        """
        Uses an ECAPA-TDNN neural network to extract a time-invariant 
        speaker embedding, then binarizes it for cryptography.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name

        try:
            # 1. AI extracts the identity (outputs a [1, 1, 192] tensor)
            # The load_audio function natively handles the sample rate conversions
            signal = self.classifier.load_audio(tmp_file_path)
            embeddings = self.classifier.encode_batch(signal)
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

        # 2. Flatten the tensor into a simple 1D numpy array of 192 floats
        vector = embeddings.squeeze().cpu().numpy()

        # 3. Binarization (Keep the median logic for cryptographic entropy)
        median_val = np.median(vector)
        binary_matrix = (vector > median_val).astype(np.uint8)

        return binary_matrix

audio_service = DeepAudioProcessor()
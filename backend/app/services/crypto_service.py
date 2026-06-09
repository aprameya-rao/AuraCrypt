import numpy as np

# Import the encoder so we can dynamically check its required length
from app.services.bch_encoder import bch_encoder
from app.services.crypto_constants import HASH_SIZE

class CryptoService:
    def __init__(self):
        # We no longer hardcode the length (e.g., 4603).
        # It will be calculated dynamically to ensure absolute 1:1 shape matching.
        pass

    def create_master_biometric_key(self, kinetic_array: np.ndarray, audio_binary: np.ndarray) -> np.ndarray:
        """
        Converts the float-based kinetic array into binary, merges it 
        with the audio array, and perfectly pads/truncates it to match the BCH codeword.
        """
        # 1. Binarize the Kinetic Data using the median threshold
        if len(kinetic_array) > 0:
            median_val = np.median(kinetic_array)
            kinetic_binary = (kinetic_array > median_val).astype(np.uint8)
        else:
            kinetic_binary = np.array([], dtype=np.uint8)

        # 2. Concatenate them together
        raw_master_key = np.concatenate((kinetic_binary, audio_binary))
        
        # 3. Determine EXACT target length required by the BCH Encoder
        # By passing a dummy 256-bit array, we mathematically guarantee the sizes will match
        dummy_hash = np.zeros(256, dtype=np.uint8)
        target_length = len(bch_encoder.encode(dummy_hash))
        
        # 4. THE PADDING FIX (Looping strategy for entropy preservation)
        current_length = len(raw_master_key)
        padding_needed = target_length - current_length
        
        if padding_needed > 0:
            # We "loop" the array to maintain the natural biometric noise distribution.
            # Using np.resize is a bulletproof way to loop the array as many times
            # as needed without throwing an index error.
            padding_bits = np.resize(raw_master_key, padding_needed)
            final_master_key = np.concatenate((raw_master_key, padding_bits))
            
        elif padding_needed < 0:
            # Truncate if the raw biometrics somehow exceeded the BCH codeword size
            final_master_key = raw_master_key[:target_length]
            
        else:
            final_master_key = raw_master_key
            
        return final_master_key

    def left_rotate(self, value: int, shift: int) -> int:
        """Helper for the Hash: Circular bitwise left rotation for 32-bit integers."""
        return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF

    def titan_hash_password(self, password: str, output_bits:int= HASH_SIZE) -> np.ndarray:
        """
        A custom ARX (Add-Rotate-XOR) cryptographic hash function built from scratch.
        Takes a string password and returns a strictly sized 1D NumPy array of 0s and 1s.
        """
        # 1. Convert password to raw bytes
        pwd_bytes = password.encode('utf-8')
        
        # 2. Initialize State: 8 blocks of 32-bit integers (Fractional parts of square roots of primes)
        state = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

        # 3. Phase 1 Mixing: Inject the password bytes into the state
        for i, byte in enumerate(pwd_bytes):
            state_idx = i % 8
            # Add
            state[state_idx] = (state[state_idx] + byte) & 0xFFFFFFFF
            # Rotate
            state[state_idx] = self.left_rotate(state[state_idx], 7)
            # XOR with adjacent block
            state[(i + 1) % 8] ^= state[state_idx]

        # 4. Phase 2 Avalanche: 24 rounds of intense mathematical scrambling
        for round_num in range(24):
            for i in range(8):
                # Add to neighbor
                state[i] = (state[i] + state[(i + 1) % 8]) & 0xFFFFFFFF
                # Rotate by prime numbers to maximize diffusion
                state[i] = self.left_rotate(state[i], 13 if round_num % 2 == 0 else 17)
                # XOR with opposite neighbor
                state[i] ^= state[(i + 4) % 8]

        # 5. Binarization: Convert the 8 32-bit integers into a pure string of 256 bits
        bit_string = ''.join([format(s, '032b') for s in state])
        
        # 6. Formatting: Convert to our standard NumPy array of 0s and 1s
        final_hash_array = np.array([int(b) for b in bit_string[:output_bits]], dtype=np.uint8)
        
        return final_hash_array

crypto_service = CryptoService()
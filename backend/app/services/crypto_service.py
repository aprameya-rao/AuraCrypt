import numpy as np

class CryptoService:
    def __init__(self):
        # We need our biometric key length to perfectly match our future Error-Corrected Password
        self.master_key_length = 4876

    def create_master_biometric_key(self, kinetic_array: np.ndarray, audio_binary: np.ndarray) -> np.ndarray:
        """
        Converts the float-based kinetic array into binary, merges it 
        with the audio array, and pads it to strictly 4,216 bits.
        """
        # 1. Binarize the Kinetic Data using the median threshold
        median_val = np.median(kinetic_array)
        kinetic_binary = (kinetic_array > median_val).astype(np.uint8)

        # 2. Concatenate them together (This yields exactly 3,296 bits)
        raw_master_key = np.concatenate((kinetic_binary, audio_binary))
        
        # 3. THE PADDING FIX: Stretch the array to 4,216 bits
        current_length = len(raw_master_key)
        padding_needed = self.master_key_length - current_length
        
        if padding_needed > 0:
            # We "loop" the array by grabbing the first 920 bits and attaching them to the end.
            # This ensures the padded section carries the exact same natural 10% noise rate.
            padding_bits = raw_master_key[:padding_needed]
            final_master_key = np.concatenate((raw_master_key, padding_bits))
        else:
            final_master_key = raw_master_key[:self.master_key_length]
            
        return final_master_key
    

    def left_rotate(self, value: int, shift: int) -> int:
        """Helper for the Hash: Circular bitwise left rotation for 32-bit integers."""
        return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF

    def titan_hash_password(self, password: str, output_bits: int = 256) -> np.ndarray:
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
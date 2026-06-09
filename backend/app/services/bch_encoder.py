import numpy as np
from app.services.crypto_constants import HASH_SIZE, ERROR_ALLOWANCE_T, GALOIS_FIELD_M, GENERATOR_POLY
class BCHEncoder:
    def __init__(self, message_bits=HASH_SIZE, error_allowance=ERROR_ALLOWANCE_T):
        self.k = message_bits
        self.t = error_allowance
        self.m = GALOIS_FIELD_M 
        
        # Load the massive array directly from memory via the constants file
        self.generator_poly = GENERATOR_POLY
        self.parity_length = len(self.generator_poly) - 1 
        self.n = self.k + self.parity_length

    def encode(self, password_hash: np.ndarray) -> np.ndarray:
        """
        Takes the 256-bit password hash and encodes it into a 4,216-bit Codeword 
        using binary polynomial division.
        """
        if len(password_hash) != self.k:
            raise ValueError(f"Password hash must be exactly {self.k} bits.")

        # 1. Create the codeword template: [ Password Hash (256) | Zeros (3960) ]
        codeword = np.zeros(self.n, dtype=np.uint8)
        codeword[:self.k] = password_hash
        
        # 2. Binary Polynomial Long Division (LFSR Method)
        # We make a copy of the password hash to act as our working "dividend"
        remainder = np.copy(codeword)
        
        # We iterate through the message bits. If the leading bit is a 1, 
        # we XOR the generator polynomial against it.
        for i in range(self.k):
            if remainder[i] == 1:
                # XOR the generator polynomial across the current window
                # g(x) is XORed against the remainder starting at index i
                remainder[i : i + len(self.generator_poly)] ^= self.generator_poly
                
        # 3. After the loop, the first 256 bits of 'remainder' are all 0.
        # The last 3,960 bits contain the actual mathematical parity!
        parity_bits = remainder[self.k :]
        
        # 4. Attach the parity to the original password hash to form the final Codeword
        final_codeword = np.zeros(self.n, dtype=np.uint8)
        final_codeword[:self.k] = password_hash
        final_codeword[self.k:] = parity_bits
        
        return final_codeword

# Global instance for the CryptoService to use
bch_encoder = BCHEncoder()
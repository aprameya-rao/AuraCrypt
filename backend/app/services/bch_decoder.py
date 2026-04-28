import numpy as np
from app.services.bch_galois_field import gf_engine

class BCHDecoder:
    def __init__(self, message_bits=256, error_allowance=330):
        self.k = message_bits
        self.t = error_allowance
        self.m = 12
        self.parity_length = self.t * self.m
        self.n = self.k + self.parity_length  # 4216 total bits

    def _calculate_syndromes(self, corrupted_codeword: np.ndarray) -> np.ndarray:
        """
        Phase 1: Calculate the 2t syndromes.
        If all syndromes are 0, there are no errors in the codeword!
        """
        syndromes = np.zeros(2 * self.t + 1, dtype=np.int32)
        has_error = False

        # Evaluate the codeword polynomial at roots alpha^1, alpha^2 ... alpha^2t
        for i in range(1, 2 * self.t + 1):
            root = gf_engine.exp_table[i]
            eval_result = 0
            
            # Plug the root into the polynomial using Galois math
            for j in range(self.n):
                if corrupted_codeword[j] == 1:
                    # eval_result += root^j
                    power = gf_engine.power(root, j)
                    eval_result = gf_engine.add(eval_result, power)
            
            syndromes[i] = eval_result
            if eval_result != 0:
                has_error = True

        return syndromes, has_error

    def _berlekamp_massey(self, syndromes: np.ndarray) -> np.ndarray:
        """
        Phase 2: The Berlekamp-Massey Algorithm.
        Converts the syndromes into an Error Locator Polynomial (Sigma).
        """
        # Initialize polynomials: Sigma (current) and B (previous)
        sigma = np.zeros(self.t + 1, dtype=np.int32)
        b_poly = np.zeros(self.t + 1, dtype=np.int32)
        
        sigma[0] = 1
        b_poly[0] = 1
        
        l = 0  # Current number of errors assumed
        m = 1  # Shift tracker

        for i in range(1, 2 * self.t + 1):
            # Calculate the discrepancy (Delta)
            delta = syndromes[i]
            for j in range(1, l + 1):
                term = gf_engine.multiply(sigma[j], syndromes[i - j])
                delta = gf_engine.add(delta, term)

            if delta == 0:
                m += 1
            else:
                # Store a copy of sigma before we update it
                old_sigma = np.copy(sigma)
                
                # sigma(x) = sigma(x) - delta * x^m * b(x)
                for j in range(self.t + 1 - m):
                    term = gf_engine.multiply(delta, b_poly[j])
                    sigma[j + m] = gf_engine.add(sigma[j + m], term)

                if 2 * l <= i - 1:
                    l = i - l
                    # b(x) = old_sigma(x) / delta
                    delta_inv = gf_engine.inverse(delta)
                    for j in range(self.t + 1):
                        b_poly[j] = gf_engine.multiply(old_sigma[j], delta_inv)
                    m = 1
                else:
                    m += 1

        # The degree of the sigma polynomial tells us how many errors we found
        error_count = l
        return sigma, error_count

    def _chien_search(self, sigma: np.ndarray, error_count: int) -> list:
        """
        Phase 3: The Chien Search.
        Finds the roots of the Sigma polynomial. The index of a root 
        corresponds directly to the index of a flipped bit!
        """
        error_positions = []
        
        # Test every single bit position in the 4216-bit codeword
        for i in range(self.n):
            # Test root alpha^(-i)
            root_inverse = gf_engine.exp_table[gf_engine.field_size - i]
            eval_result = 0
            
            for j in range(self.t + 1):
                if sigma[j] != 0:
                    term = gf_engine.multiply(sigma[j], gf_engine.power(root_inverse, j))
                    eval_result = gf_engine.add(eval_result, term)
            
            # If the polynomial evaluates to 0, we found an error at index i
            if eval_result == 0:
                error_positions.append(i)
                
                # Optimization: Stop searching if we've found all the errors
                if len(error_positions) == error_count:
                    break

        return error_positions

    def decode(self, corrupted_codeword: np.ndarray) -> np.ndarray:
        """
        The Master Function. Orchestrates the 3 phases to fix the errors 
        and extract the perfectly restored 256-bit password hash.
        """
        if len(corrupted_codeword) != self.n:
            raise ValueError(f"Codeword must be exactly {self.n} bits.")

        # Step 1: Check for errors
        syndromes, has_error = self._calculate_syndromes(corrupted_codeword)
        
        if not has_error:
            # Perfection! No errors to fix. Just slice off the first 256 bits.
            return corrupted_codeword[:self.k]

        # Step 2: Generate Error Locator Polynomial
        sigma, error_count = self._berlekamp_massey(syndromes)

        # Security/Math check: If the algorithm detects more errors than our limit,
        # or the math collapses, decoding fails entirely.
        if error_count > self.t:
            raise ValueError("Too much noise! Error limit exceeded. Access Denied.")

        # Step 3: Find the exact broken bits
        error_positions = self._chien_search(sigma, error_count)

        if len(error_positions) != error_count:
            # This happens if there are so many errors that it "tricks" the BMA
            # into thinking there are fewer errors than there actually are.
            raise ValueError("Uncorrectable error pattern detected. Access Denied.")

        # Step 4: The Final Fix
        corrected_codeword = np.copy(corrupted_codeword)
        for pos in error_positions:
            corrected_codeword[pos] ^= 1  # Flip the bit back (0->1 or 1->0)

        # Extract and return the perfectly restored 256-bit password hash
        restored_password_hash = corrected_codeword[:self.k]
        
        return restored_password_hash

# Global instance for the CryptoService
bch_decoder = BCHDecoder()
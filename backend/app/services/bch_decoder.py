import numpy as np
import multiprocessing
from app.services.bch_galois_field import gf_engine
from app.services.crypto_constants import HASH_SIZE, ERROR_ALLOWANCE_T, GALOIS_FIELD_M, PARITY_LENGTH, CODEWORD_LENGTH
import time


# =====================================================================
# INDEPENDENT WORKERS (Extracted globally to allow multiprocessing Pickling)
# =====================================================================

def _syndrome_worker(args):
    """
    Parallel Worker for Syndrome Calculation. Evaluates a chunk of roots.
    """
    start_root, end_root, corrupted_codeword, n = args
    local_syndromes = {}
    
    for i in range(start_root, end_root):
        root = gf_engine.exp_table[i]
        eval_result = 0
        
        for j in range(n):
            if corrupted_codeword[j] == 1:
                power = gf_engine.power(root, j)
                eval_result = gf_engine.add(eval_result, power)
                
        local_syndromes[i] = eval_result
        
    return local_syndromes


def _chien_worker(args):
    """
    Parallel Worker for Chien Search. Sweeps a chunk of the codeword bits.
    """
    start_bit, end_bit, sigma, t = args
    local_errors = []
    field_size = gf_engine.field_size
    
    for i in range(start_bit, end_bit):
        root_inverse = gf_engine.exp_table[field_size - i]
        eval_result = 0
        
        for j in range(t + 1):
            if sigma[j] != 0:
                term = gf_engine.multiply(sigma[j], gf_engine.power(root_inverse, j))
                eval_result = gf_engine.add(eval_result, term)
                
        if eval_result == 0:
            local_errors.append(i)
            
    return local_errors


# =====================================================================
# CORE DECODER CLASS
# =====================================================================

class BCHDecoder:
    def __init__(self, message_bits=HASH_SIZE, error_allowance=ERROR_ALLOWANCE_T):
        self.k = message_bits
        self.t = error_allowance
        self.m = GALOIS_FIELD_M
        self.parity_length = PARITY_LENGTH  
        self.n = CODEWORD_LENGTH

    def _calculate_syndromes(self, corrupted_codeword: np.ndarray) -> tuple[np.ndarray, bool]:
        """
        Phase 1: Multi-Core Syndrome Calculation.
        """
        syndromes = np.zeros(2 * self.t + 1, dtype=np.int32)
        has_error = False
        
        # Determine total roots to check (from 1 to 2t)
        total_roots = 2 * self.t
        cpu_cores = multiprocessing.cpu_count()
        
        # Split root checking work across cores
        chunk_size = max(1, total_roots // cpu_cores)
        ranges = []
        
        for i in range(cpu_cores):
            start = 1 + (i * chunk_size)
            end = (1 + total_roots) if i == cpu_cores - 1 else 1 + ((i + 1) * chunk_size)
            if start < end:
                ranges.append((start, end, corrupted_codeword, self.n))
                
        with multiprocessing.Pool(processes=len(ranges)) as pool:
            results = pool.map(_syndrome_worker, ranges)
            
        # Merge individual processes' dictionaries into the master array
        for local_dict in results:
            for idx, val in local_dict.items():
                syndromes[idx] = val
                if val != 0:
                    has_error = True

        return syndromes, has_error

    def _berlekamp_massey(self, syndromes: np.ndarray) -> tuple[np.ndarray, int]:
        """
        Phase 2: The Berlekamp-Massey Algorithm (Inherently sequential).
        """
        sigma = np.zeros(self.t + 1, dtype=np.int32)
        b_poly = np.zeros(self.t + 1, dtype=np.int32)
        
        sigma[0] = 1
        b_poly[0] = 1
        
        l = 0  
        m = 1  

        for i in range(1, 2 * self.t + 1):
            delta = syndromes[i]
            for j in range(1, l + 1):
                term = gf_engine.multiply(sigma[j], syndromes[i - j])
                delta = gf_engine.add(delta, term)

            if delta == 0:
                m += 1
            else:
                old_sigma = np.copy(sigma)
                for j in range(self.t + 1 - m):
                    term = gf_engine.multiply(delta, b_poly[j])
                    sigma[j + m] = gf_engine.add(sigma[j + m], term)

                if 2 * l <= i - 1:
                    l = i - l
                    delta_inv = gf_engine.inverse(delta)
                    for j in range(self.t + 1):
                        b_poly[j] = gf_engine.multiply(old_sigma[j], delta_inv)
                    m = 1
                else:
                    m += 1

        error_count = l
        return sigma, error_count

    def _chien_search(self, sigma: np.ndarray, error_count: int) -> list:
        """
        Phase 3: Multi-Core Chien Search.
        Splits the search space dynamically across every available hardware core.
        """
        cpu_cores = multiprocessing.cpu_count()
        chunk_size = self.n // cpu_cores
        ranges = []
        
        for i in range(cpu_cores):
            start = i * chunk_size
            end = self.n if i == cpu_cores - 1 else (i + 1) * chunk_size
            ranges.append((start, end, sigma, self.t))
            
        error_positions = []
        
        with multiprocessing.Pool(processes=cpu_cores) as pool:
            results = pool.map(_chien_worker, ranges)
            
        for res in results:
            error_positions.extend(res)
            
        return error_positions

    def decode(self, corrupted_codeword: np.ndarray) -> np.ndarray:
        """
        Master Function orchestration.
        """

        start_decoding_time = time.perf_counter()
        
        if len(corrupted_codeword) != self.n:
            raise ValueError(f"Codeword must be exactly {self.n} bits.")

        aligned_codeword = corrupted_codeword[::-1]
        
        # Step 1: Parallel Syndrome Validation
        syndromes, has_error = self._calculate_syndromes(aligned_codeword)
        
        if not has_error:
            return aligned_codeword[::-1][:self.k]

        # Step 2: Sequence-dependent error modeling
        sigma, error_count = self._berlekamp_massey(syndromes)

        if error_count > self.t:
            raise ValueError("Too much noise! Error limit exceeded. Access Denied.")

        # Step 3: Parallel search for bit flips
        error_positions = self._chien_search(sigma, error_count)

        if len(error_positions) != error_count:
            raise ValueError("Uncorrectable error pattern detected. Access Denied.")

        # Step 4: Bit Correction
        corrected_codeword = np.copy(aligned_codeword)
        for pos in error_positions:
            corrected_codeword[pos] ^= 1  

        final_codeword = corrected_codeword[::-1]
        return final_codeword[:self.k]

# Global instance for the CryptoService
bch_decoder = BCHDecoder()
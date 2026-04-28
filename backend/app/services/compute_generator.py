import numpy as np
import time
from bch_galois_field import gf_engine

def poly_mult_gf(p1: list, p2: list) -> list:
    """Multiplies two polynomials using Galois Field arithmetic."""
    result = [0] * (len(p1) + len(p2) - 1)
    for i in range(len(p1)):
        for j in range(len(p2)):
            # Multiply coefficients in GF
            term = gf_engine.multiply(p1[i], p2[j])
            # Add (XOR) to the resulting polynomial
            result[i+j] = gf_engine.add(result[i+j], term)
    return result
    
    
def compute_bch_generator(t=330, field_size=16383):
    print(f"Starting computation for t={t} errors in GF(2^12)...")
    start_time = time.time()
    
    # 1. Group the roots into Cyclotomic Cosets
    # We need to cover roots alpha^1 through alpha^(2t)
    required_roots = set(range(1, 2 * t + 1))
    cosets = []
    processed = set()
    
    for i in range(1, 2 * t + 1):
        if i not in processed:
            coset = set()
            current = i
            # Roots multiply by 2 (modulo field size) in binary fields
            while current not in coset:
                coset.add(current)
                processed.add(current)
                current = (current * 2) % field_size
            cosets.append(coset)
            
    print(f"Found {len(cosets)} unique minimal polynomials to multiply.")

    # 2. Compute the final Generator Polynomial g(x)
    # We start with g(x) = 1 (represented as array [1])
    g_x = [1]
    
    for idx, coset in enumerate(cosets):
        # Build the minimal polynomial for this coset
        # M(x) = (x - alpha^r1) * (x - alpha^r2) ...
        # In GF(2), subtraction is addition: (x + alpha^r)
        # Represented as array [1, alpha^r]
        m_x = [1]
        for root in coset:
            root_val = gf_engine.exp_table[root]
            # Multiply m_x by (x + root_val) -> array [1, root_val]
            m_x = poly_mult_gf(m_x, [1, root_val])
            
        # Multiply the global g(x) by this new minimal polynomial
        g_x = poly_mult_gf(g_x, m_x)
        
        if (idx + 1) % 10 == 0:
            print(f"Computed {idx + 1}/{len(cosets)} polynomials...")

    end_time = time.time()
    print(f"\nComputation Complete! Time: {round(end_time - start_time, 2)} seconds")
    print(f"Generator Polynomial Length: {len(g_x)} bits.")
    
    return g_x

if __name__ == "__main__":
    # Compute the polynomial
    generator = compute_bch_generator(t=330)
    
    # Save it to a text file so you can copy-paste it
    with open("true_generator_poly.txt", "w") as f:
        f.write(f"[{', '.join(map(str, generator))}]")
    
    print("Successfully saved to 'true_generator_poly.txt'.")
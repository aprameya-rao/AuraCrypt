import numpy as np

class GaloisField:
    def __init__(self, m=14):
        """
        Initializes the Galois Field GF(2^m).
        For our 3,296-bit biometric key, we use m=12 (which supports up to 4095 bits).
        """
        self.m = m
        self.field_size = (1 << m) - 1  # 16383
        
        # The primitive polynomial is what forces the math to "wrap around" 
        # when a number gets too big. For GF(2^12), the standard integer 
        # representation of the polynomial (x^12 + x^6 + x^4 + x + 1) is 4179.
        self.primitive_poly = 16427
        
        # Pre-compute lookup tables for blazing fast math
        self.exp_table = np.zeros(self.field_size * 2, dtype=np.int32)
        self.log_table = np.zeros(self.field_size + 1, dtype=np.int32)
        
        self._generate_tables()

    def _generate_tables(self):
        """
        Generates the exponential and logarithm tables. 
        This is run once upon initialization.
        """
        x = 1
        for i in range(self.field_size):
            self.exp_table[i] = x
            self.log_table[x] = i
            
            x <<= 1  # Multiply by alpha (shift left by 1 bit)
            
            # If the number exceeds 12 bits, apply the polynomial XOR to wrap it back
            if x & (1 << self.m):
                x ^= self.primitive_poly

        # Double the exp_table size to prevent index out-of-bounds 
        # when we add two logs together later.
        for i in range(self.field_size):
            self.exp_table[i + self.field_size] = self.exp_table[i]

    def add(self, a: int, b: int) -> int:
        """
        Addition and Subtraction in GF(2^m) are identical.
        They are both simply a bitwise XOR operation.
        """
        return a ^ b

    def multiply(self, a: int, b: int) -> int:
        """
        Multiplies two numbers using the log tables.
        Instead of complex polynomial multiplication, we just add their logs!
        """
        if a == 0 or b == 0:
            return 0
        
        # a * b = exp(log(a) + log(b))
        log_sum = self.log_table[a] + self.log_table[b]
        return self.exp_table[log_sum]

    def divide(self, a: int, b: int) -> int:
        """
        Divides two numbers using the log tables.
        a / b = a * (1/b) = exp(log(a) - log(b))
        """
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero in Galois Field.")
        if a == 0:
            return 0
        
        # Add field_size to ensure the subtraction doesn't result in a negative index
        log_diff = (self.log_table[a] - self.log_table[b] + self.field_size) % self.field_size
        return self.exp_table[log_diff]

    def inverse(self, a: int) -> int:
        """
        Finds the multiplicative inverse of a number.
        (What number multiplied by 'a' equals 1?)
        """
        if a == 0:
            raise ZeroDivisionError("Zero has no inverse in Galois Field.")
        
        return self.exp_table[self.field_size - self.log_table[a]]

    def power(self, a: int, power: int) -> int:
        """Raises a number 'a' to a given power."""
        if a == 0:
            return 0
        if power == 0:
            return 1
            
        # a^power = exp(log(a) * power mod field_size)
        log_pow = (self.log_table[a] * power) % self.field_size
        return self.exp_table[log_pow]

# Instantiate a global engine for the rest of our cryptography to use
gf_engine = GaloisField()
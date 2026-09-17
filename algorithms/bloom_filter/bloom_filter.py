"""
==============================================================================
SHOPLYTICS: Distributed Big Data Analytics Platform for E-Commerce
ALGORITHM: Bloom Filter (Space-Efficient Probabilistic Membership Testing)
==============================================================================

WHAT IT DOES:
A Bloom Filter is a space-efficient probabilistic data structure used to test 
whether an element is a member of a set. It guarantees:
- NO False Negatives: If it returns False, the element is DEFINITELY NOT in the set.
- Small False Positives: If it returns True, the element is PROBABLY in the set.

WHY WE NEED IT IN SHOPLYTICS:
In high-throughput e-commerce systems (like Amazon, Flipkart, or Olist), millions of
queries per second check if a product exists, if a discount code is valid, or if
a transaction/user ID is on a blocklist. Querying slow persistent storage (HDFS,
NoSQL, Disk) for millions of non-existent items causes disk thrashing and high latency.
A Bloom Filter acts as a lightning-fast in-memory cache filter:
- If Bloom Filter returns False -> Instantly reject without touching database/HDFS.
- If Bloom Filter returns True  -> Fetch actual record from database/HDFS.

WHERE IT FITS:
Data Source -> In-Memory Bloom Filter Cache -> Fast-Path Filter -> NoSQL / HDFS
==============================================================================
"""

import os
import sys
import math
import time
import uuid
import hashlib
import pandas as pd
import numpy as np


class BloomFilter:
    """
    Standard Probabilistic Bloom Filter implementation using Double Hashing.
    Formula for generating k hash indices:
        h_i(x) = (hash1(x) + i * hash2(x)) % m
    where:
        m = size of bit array
        k = number of hash functions
        n = expected number of elements
        p = target false positive probability
    """

    def __init__(self, expected_elements: int, false_positive_rate: float = 0.01):
        """
        Initializes the Bloom Filter with mathematically optimal bit size (m)
        and number of hash functions (k).
        """
        if expected_elements <= 0:
            raise ValueError("Expected elements must be greater than 0")
        if not (0 < false_positive_rate < 1):
            raise ValueError("False positive rate must be between 0 and 1")

        self.n = expected_elements
        self.p = false_positive_rate

        # Optimal bit array size: m = - (n * ln(p)) / (ln(2)^2)
        self.m = self.calculate_optimal_m(self.n, self.p)

        # Optimal number of hash functions: k = (m / n) * ln(2)
        self.k = self.calculate_optimal_k(self.m, self.n)

        # Bytearray representation: each byte holds 8 bits
        self.byte_count = math.ceil(self.m / 8)
        self.bit_array = bytearray(self.byte_count)

        # Counter for inserted elements
        self.inserted_count = 0

    @staticmethod
    def calculate_optimal_m(n: int, p: float) -> int:
        """Calculates optimal bit array size m."""
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return int(math.ceil(m))

    @staticmethod
    def calculate_optimal_k(m: int, n: int) -> int:
        """Calculates optimal number of hash functions k."""
        k = (m / n) * math.log(2)
        return max(1, int(round(k)))

    def _get_hashes(self, item: str):
        """
        Generates k independent hash values using double hashing:
        MD5 (hash1) + SHA256 (hash2).
        This provides uniform distribution and avoids needing k separate hash algorithms.
        """
        item_bytes = str(item).encode('utf-8')

        # Primary hash (MD5 -> 64-bit integer slice)
        h1 = int(hashlib.md5(item_bytes).hexdigest()[:16], 16)

        # Secondary hash (SHA256 -> 64-bit integer slice)
        h2 = int(hashlib.sha256(item_bytes).hexdigest()[:16], 16)

        # Generate k bit indices
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item: str) -> None:
        """Adds an item to the Bloom Filter by setting k bits to 1."""
        for bit_index in self._get_hashes(item):
            byte_index = bit_index // 8
            bit_offset = bit_index % 8
            self.bit_array[byte_index] |= (1 << bit_offset)
        self.inserted_count += 1

    def contains(self, item: str) -> bool:
        """
        Tests whether an item is possibly in the set.
        Returns:
            False: The item is DEFINITELY NOT in the set (0% False Negatives).
            True:  The item is PROBABLY in the set (may be False Positive).
        """
        for bit_index in self._get_hashes(item):
            byte_index = bit_index // 8
            bit_offset = bit_index % 8
            if not (self.bit_array[byte_index] & (1 << bit_offset)):
                return False
        return True

    def count_bits_set(self) -> int:
        """Counts total number of bits currently set to 1 in the bit array."""
        return sum(bin(byte).count('1') for byte in self.bit_array)

    def current_fill_ratio(self) -> float:
        """Returns the fraction of bits set to 1."""
        return self.count_bits_set() / self.m

    def theoretical_false_positive_rate(self) -> float:
        """
        Calculates theoretical false positive rate based on current insertions:
        P(FP) ≈ (1 - e^(-k * n / m))^k
        """
        if self.m == 0:
            return 1.0
        exponent = - (self.k * self.inserted_count) / self.m
        return (1.0 - math.exp(exponent)) ** self.k


# ==============================================================================
# MAIN EXECUTION & BENCHMARKING PIPELINE
# ==============================================================================

def main():
    print("============================================================")
    print("       SHOPLYTICS: BLOOM FILTER ALGORITHM EXECUTION         ")
    print("============================================================")

    # 1. Load Dataset
    input_file = r"C:\Projects\Shoplytics\data\processed\products_clean.csv"
    print(f"\n[STEP 1] Loading Olist Products Dataset...")
    print(f"File Path: {input_file}")

    if not os.path.exists(input_file):
        print(f"ERROR: File not found at {input_file}")
        sys.exit(1)

    df_products = pd.read_csv(input_file)
    product_ids = df_products["product_id"].dropna().astype(str).unique().tolist()
    total_unique_products = len(product_ids)

    print(f"Total rows in dataset       : {len(df_products):,}")
    print(f"Total unique product IDs (n): {total_unique_products:,}")

    # 2. Configure Bloom Filter
    target_fpr = 0.01  # Target 1% False Positive Rate
    print(f"\n[STEP 2] Initializing Bloom Filter Configuration...")
    print(f"Target False Positive Rate (p) : {target_fpr * 100:.2f} %")

    bf = BloomFilter(expected_elements=total_unique_products, false_positive_rate=target_fpr)

    print(f"Optimal Bit Array Size (m)     : {bf.m:,} bits ({bf.m / 8 / 1024:.2f} KB)")
    print(f"Optimal Hash Functions (k)     : {bf.k}")
    print(f"Allocated Memory in Bytes      : {bf.byte_count:,} bytes")

    # 3. Insertion Benchmark
    print(f"\n[STEP 3] Inserting {total_unique_products:,} Product IDs into Bloom Filter...")
    start_insert = time.perf_counter()
    for pid in product_ids:
        bf.add(pid)
    end_insert = time.perf_counter()

    insert_time_ms = (end_insert - start_insert) * 1000
    insert_throughput = total_unique_products / (end_insert - start_insert)

    print(f"Insertion Completed in         : {insert_time_ms:.2f} ms")
    print(f"Insertion Throughput           : {insert_throughput:,.0f} ops/sec")
    print(f"Bits set to 1 in bit array     : {bf.count_bits_set():,} / {bf.m:,} ({bf.current_fill_ratio() * 100:.2f}%)")

    # 4. Membership Verification: Ground-Truth Existing Items (False Negative Test)
    test_existing_count = min(10000, total_unique_products)
    test_existing_sample = product_ids[:test_existing_count]

    print(f"\n[STEP 4] Testing Existing Elements Lookup ({test_existing_count:,} queries)...")
    start_exist_test = time.perf_counter()
    true_positives = 0
    false_negatives = 0

    for pid in test_existing_sample:
        if bf.contains(pid):
            true_positives += 1
        else:
            false_negatives += 1
    end_exist_test = time.perf_counter()

    lookup_existing_time_ms = (end_exist_test - start_exist_test) * 1000
    print(f"True Positives (Correctly identified) : {true_positives:,}")
    print(f"False Negatives (Should ALWAYS be 0)  : {false_negatives}")
    print(f"False Negative Rate                   : {(false_negatives / test_existing_count) * 100:.4f} %")
    assert false_negatives == 0, "Critical Failure: Bloom Filter produced False Negatives!"

    # 5. Membership Verification: Non-Existing Synthetic Items (False Positive Test)
    non_existing_test_count = 50000
    print(f"\n[STEP 5] Testing Non-Existing Elements Lookup ({non_existing_test_count:,} queries)...")

    # Generate synthetic random UUIDs that do not exist in product catalog
    existing_set = set(product_ids)
    synthetic_non_existing = []
    while len(synthetic_non_existing) < non_existing_test_count:
        fake_id = uuid.uuid4().hex
        if fake_id not in existing_set:
            synthetic_non_existing.append(fake_id)

    start_non_exist_test = time.perf_counter()
    false_positives = 0
    true_negatives = 0

    for fake_id in synthetic_non_existing:
        if bf.contains(fake_id):
            false_positives += 1
        else:
            true_negatives += 1
    end_non_exist_test = time.perf_counter()

    lookup_non_exist_time_ms = (end_non_exist_test - start_non_exist_test) * 1000
    empirical_fpr = (false_positives / non_existing_test_count) * 100
    theoretical_fpr = bf.theoretical_false_positive_rate() * 100

    print(f"True Negatives (Correctly rejected)   : {true_negatives:,}")
    print(f"False Positives (Incorrectly accepted): {false_positives:,}")
    print(f"Empirical False Positive Rate (FPR)   : {empirical_fpr:.4f} %")
    print(f"Theoretical False Positive Rate (FPR) : {theoretical_fpr:.4f} %")

    # 6. Memory Footprint Comparison (Big Data Advantage)
    # Estimate standard Python set/hash table memory vs Bloom Filter bit array
    raw_strings_memory_bytes = sys.getsizeof(product_ids) + sum(sys.getsizeof(pid) for pid in product_ids)
    python_set_memory_bytes = sys.getsizeof(set(product_ids)) + sum(sys.getsizeof(pid) for pid in product_ids)
    bloom_filter_memory_bytes = bf.byte_count + sys.getsizeof(bf.bit_array)

    memory_savings_pct = ((python_set_memory_bytes - bloom_filter_memory_bytes) / python_set_memory_bytes) * 100

    print(f"\n[STEP 6] Memory Efficiency Analysis:")
    print(f"Python Set Storage Size               : {python_set_memory_bytes / 1024:.2f} KB ({python_set_memory_bytes / (1024*1024):.2f} MB)")
    print(f"Bloom Filter Storage Size             : {bloom_filter_memory_bytes / 1024:.2f} KB ({bloom_filter_memory_bytes / (1024*1024):.4f} MB)")
    print(f"Memory Reduction / Savings            : {memory_savings_pct:.2f} %")

    # 7. Save Results Locally
    output_dir = r"C:\Projects\Shoplytics\results\bloom_filter"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "bloom_filter_results.csv")

    summary_data = [{
        "total_unique_products": total_unique_products,
        "target_fpr_percent": target_fpr * 100,
        "bit_array_size_m": bf.m,
        "hash_functions_k": bf.k,
        "bits_set_count": bf.count_bits_set(),
        "bit_fill_ratio_percent": round(bf.current_fill_ratio() * 100, 2),
        "test_existing_queries": test_existing_count,
        "true_positives": true_positives,
        "false_negatives": false_negatives,
        "false_negative_rate_percent": 0.0,
        "test_non_existing_queries": non_existing_test_count,
        "true_negatives": true_negatives,
        "false_positives": false_positives,
        "empirical_fpr_percent": round(empirical_fpr, 4),
        "theoretical_fpr_percent": round(theoretical_fpr, 4),
        "bloom_filter_size_kb": round(bloom_filter_memory_bytes / 1024, 2),
        "python_set_size_kb": round(python_set_memory_bytes / 1024, 2),
        "memory_savings_percent": round(memory_savings_pct, 2),
        "insertion_throughput_ops_sec": round(insert_throughput, 2)
    }]

    df_results = pd.DataFrame(summary_data)
    df_results.to_csv(output_file, index=False)

    print("\n============================================================")
    print("BLOOM FILTER RESULTS SUMMARY")
    print("============================================================")
    for col, val in summary_data[0].items():
        print(f"{col:<32}: {val}")

    print("\n============================================================")
    print("BLOOM FILTER EXECUTION COMPLETED SUCCESSFULLY")
    print("============================================================")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()

"""
==============================================================================
SHOPLYTICS: Distributed Big Data Analytics Platform for E-Commerce
ALGORITHM: Flajolet-Martin (Probabilistic Distinct Elements Counting in Streams)
==============================================================================

WHAT IT DOES:
The Flajolet-Martin (FM) algorithm is a classic streaming algorithm designed to 
estimate the number of DISTINCT elements (cardinality) in a massive data stream 
using only a tiny fixed amount of memory (O(log N) space).

WHY WE NEED IT IN SHOPLYTICS:
In high-volume e-commerce platforms (like Amazon, Flipkart, or Olist), millions of 
customer interactions, page views, and orders stream in continuously. Answering 
questions like "How many unique customers made purchases?" or "How many distinct 
active shoppers visited today?" using exact hash sets requires storing every single 
identifier in memory, which scales to gigabytes of RAM.
The Flajolet-Martin algorithm provides an accurate approximation using mere bytes 
of register memory.

WHERE IT FITS:
Data Stream (Customer Transactions) -> Hash Bitmaps -> FM Estimator -> Analytics/Dashboard
==============================================================================
"""

import os
import sys
import math
import time
import random
import hashlib
import statistics
import pandas as pd


class FlajoletMartin:
    """
    Production-grade Flajolet-Martin Distinct Count Estimator with 
    Universal Hashing and Stochastic Averaging (Median-of-Means).

    Algorithm Principles:
    1. Stream elements x are mapped through k independent 2-universal hash functions:
       h_i(x) = (a_i * hash(x) + b_i) mod p
    2. For each hash, calculate rho(h(x)) = number of trailing zeros (least significant 1-bit).
    3. Maintain a 32-bit bitmap and track:
       - R: the index of the first 0-bit in the bitmap (classic Flajolet-Martin estimate).
       - Max Rho: the highest trailing zero observed.
    4. Single estimate formula: E_i = (2^R_i) / phi, where phi = 0.77351.
    5. Group k hash functions into g groups, compute group means, and take the median of means 
       to eliminate variance and avoid extreme power-of-two outliers.
    """

    PHI = 0.77351  # Flajolet-Martin correction factor (1 / (gamma(-1/2) * sqrt(2)...))

    def __init__(self, num_hashes: int = 24, num_groups: int = 4, seed: int = 42):
        if num_hashes % num_groups != 0:
            raise ValueError("num_hashes must be divisible by num_groups")

        self.num_hashes = num_hashes
        self.num_groups = num_groups
        self.group_size = num_hashes // num_groups
        self.seed = seed

        # Large 32-bit prime for universal hashing
        self.p = 4294967291

        # Generate deterministic (a, b) parameters for universal hash family
        rng = random.Random(self.seed)
        self.hash_params = [
            (rng.randint(1, self.p - 1), rng.randint(0, self.p - 1))
            for _ in range(self.num_hashes)
        ]

        # 32-bit bitmaps for each hash function
        self.bitmaps = [[0] * 32 for _ in range(self.num_hashes)]
        # Track maximum trailing zeros (Rho)
        self.max_rho = [0] * self.num_hashes

        # Stream counter
        self.total_elements_processed = 0

    @staticmethod
    def _count_trailing_zeros(n: int) -> int:
        """Finds the 0-indexed position of the least significant 1-bit."""
        if n == 0:
            return 32
        return (n & -n).bit_length() - 1

    def _hash(self, item_str: str, hash_index: int) -> int:
        """2-Universal hash mapping string to a 32-bit integer."""
        a, b = self.hash_params[hash_index]
        # Base MD5 slice converted to 32-bit integer
        base_h = int(hashlib.md5(item_str.encode('utf-8')).hexdigest()[:8], 16)
        return (a * base_h + b) % self.p

    def process_item(self, item: str) -> None:
        """Streams a single item and updates all hash bitmaps."""
        item_str = str(item)
        self.total_elements_processed += 1

        for i in range(self.num_hashes):
            val = self._hash(item_str, i)
            tz = self._count_trailing_zeros(val)
            if tz < 32:
                self.bitmaps[i][tz] = 1
            if tz > self.max_rho[i]:
                self.max_rho[i] = tz

    def get_r_values(self) -> list:
        """
        In classic Flajolet-Martin, R is the 0-indexed position 
        of the least significant 0-bit in the bitmap.
        """
        r_values = []
        for i in range(self.num_hashes):
            bm = self.bitmaps[i]
            first_zero = 0
            while first_zero < 32 and bm[first_zero] == 1:
                first_zero += 1
            r_values.append(first_zero)
        return r_values

    def get_individual_estimates(self) -> list:
        """Computes individual raw estimates E_i = (2^R_i) / 0.77351."""
        r_values = self.get_r_values()
        return [(2 ** r) / self.PHI for r in r_values]

    def estimate(self) -> tuple:
        """
        Computes the combined FM estimate using Stochastic Averaging:
        1. Partition hash functions into g groups.
        2. Compute arithmetic mean for each group.
        3. Take median of the group means.
        """
        estimates = self.get_individual_estimates()
        group_means = []

        for g in range(self.num_groups):
            start = g * self.group_size
            end = start + self.group_size
            group_estimates = estimates[start:end]
            group_means.append(statistics.mean(group_estimates))

        combined_estimate = statistics.median(group_means)
        return combined_estimate, group_means


# ==============================================================================
# MAIN EXECUTION & BENCHMARKING PIPELINE
# ==============================================================================

def main():
    print("==========================================")
    print("   SHOPLYTICS: FLAJOLET-MARTIN ALGORITHM  ")
    print("==========================================")

    # 1. Load Dataset
    input_file = r"C:\Projects\Shoplytics\data\processed\customers_clean.csv"
    print("\n[STEP 1] Loading Olist Customer Stream Data...")
    print(f"File: {input_file}")

    if not os.path.exists(input_file):
        print(f"ERROR: Dataset file not found at {input_file}")
        sys.exit(1)

    df = pd.read_csv(input_file)
    print(f"Total rows in dataset: {len(df):,}")

    # 2. Extract Identifier Stream
    # We use customer_unique_id: the true distinct shopper identity
    stream = df["customer_unique_id"].dropna().astype(str).tolist()
    total_stream_elements = len(stream)

    # 3. Ground Truth Exact Distinct Count
    start_exact = time.perf_counter()
    exact_distinct_set = set(stream)
    exact_distinct_count = len(exact_distinct_set)
    end_exact = time.perf_counter()

    exact_time_ms = (end_exact - start_exact) * 1000
    exact_memory_bytes = sys.getsizeof(exact_distinct_set) + sum(sys.getsizeof(x) for x in exact_distinct_set)

    print(f"\n[STEP 2] Ground-Truth Exact Distinct Computation:")
    print(f"Total stream elements (N)     : {total_stream_elements:,}")
    print(f"Exact distinct elements (D)   : {exact_distinct_count:,}")
    print(f"Exact Set Memory Footprint    : {exact_memory_bytes / 1024:.2f} KB ({exact_memory_bytes / (1024*1024):.2f} MB)")
    print(f"Exact Set Computation Time    : {exact_time_ms:.2f} ms")

    # 4. Flajolet-Martin Stream Processing
    num_hashes = 24
    num_groups = 4
    fm = FlajoletMartin(num_hashes=num_hashes, num_groups=num_groups, seed=42)

    print(f"\n[STEP 3] Running Flajolet-Martin Stream Processing...")
    print(f"Number of Universal Hash Functions : {num_hashes}")
    print(f"Number of Groups (Stochastic Avg)   : {num_groups}")
    print(f"Hash Functions per Group            : {fm.group_size}")
    print(f"Flajolet-Martin Correction Factor   : {fm.PHI}")

    start_fm = time.perf_counter()
    for item in stream:
        fm.process_item(item)
    end_fm = time.perf_counter()

    fm_time_ms = (end_fm - start_fm) * 1000
    fm_throughput = total_stream_elements / (end_fm - start_fm)

    # 5. Extract FM Statistics & Estimates
    r_values = fm.get_r_values()
    individual_estimates = fm.get_individual_estimates()
    combined_estimate, group_means = fm.estimate()

    # Calculate Errors
    absolute_error = abs(exact_distinct_count - combined_estimate)
    percentage_error = (absolute_error / exact_distinct_count) * 100

    # Memory comparison
    fm_memory_bytes = sys.getsizeof(fm.bitmaps) + sum(sys.getsizeof(bm) for bm in fm.bitmaps) + sys.getsizeof(fm.max_rho)
    memory_savings_pct = ((exact_memory_bytes - fm_memory_bytes) / exact_memory_bytes) * 100

    # 6. Display Detailed Results
    print("\n==========================================")
    print("FLAJOLET-MARTIN HASH ESTIMATES")
    print("==========================================")
    for g in range(num_groups):
        start = g * fm.group_size
        end = start + fm.group_size
        print(f"\nGroup {g + 1} (Hashes {start + 1} to {end}):")
        for h_idx in range(start, end):
            print(f"  Hash {h_idx + 1:02d}: R = {r_values[h_idx]:2d}, MaxRho = {fm.max_rho[h_idx]:2d}, Raw Est = {individual_estimates[h_idx]:>10.1f}")
        print(f"  --> Group {g + 1} Mean Estimate: {group_means[g]:>10.2f}")

    print("\n==========================================")
    print("FLAJOLET-MARTIN FINAL RESULTS")
    print("==========================================")
    print(f"Total stream elements      : {total_stream_elements:,}")
    print(f"Exact distinct elements    : {exact_distinct_count:,}")
    print(f"FM estimated distinct      : {round(combined_estimate, 2):,}")
    print(f"Absolute error             : {round(absolute_error, 2):,}")
    print(f"Percentage error           : {round(percentage_error, 2)} %")
    print(f"Hash functions             : {num_hashes}")
    print(f"Maximum Rho values         : {fm.max_rho}")
    print(f"R values (first 0 index)   : {r_values}")
    print(f"Group Means                : {[round(m, 2) for m in group_means]}")
    print(f"Processing Throughput      : {fm_throughput:,.0f} elements/sec")
    print(f"Exact Set Memory           : {exact_memory_bytes / 1024:.2f} KB ({exact_memory_bytes / (1024*1024):.2f} MB)")
    print(f"FM Registers Memory        : {fm_memory_bytes / 1024:.2f} KB ({fm_memory_bytes} bytes)")
    print(f"Memory Reduction / Savings : {memory_savings_pct:.2f} %")

    # 7. Save Local Results CSV
    output_dir = r"C:\Projects\Shoplytics\results\flajolet_martin"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "flajolet_martin_results.csv")

    summary_data = [{
        "total_stream_elements": total_stream_elements,
        "exact_distinct_elements": exact_distinct_count,
        "fm_estimated_distinct": round(combined_estimate, 2),
        "absolute_error": round(absolute_error, 2),
        "percentage_error": round(percentage_error, 2),
        "hash_functions": num_hashes,
        "num_groups": num_groups,
        "correction_factor_phi": fm.PHI,
        "fm_memory_bytes": fm_memory_bytes,
        "exact_set_memory_kb": round(exact_memory_bytes / 1024, 2),
        "memory_savings_percent": round(memory_savings_pct, 2),
        "processing_throughput_ops_sec": round(fm_throughput, 2)
    }]

    df_results = pd.DataFrame(summary_data)
    df_results.to_csv(output_file, index=False)

    print("\n==========================================")
    print("FLAJOLET-MARTIN RESULTS SAVED")
    print("==========================================")
    print(f"Local file: {output_file}")


if __name__ == "__main__":
    main()

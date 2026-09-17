"""
==============================================================================
SHOPLYTICS: Distributed Big Data Analytics Platform for E-Commerce
ALGORITHM: Cosine Similarity (Customer-to-Customer Purchase Vector Similarity)
==============================================================================

WHAT IT DOES:
Cosine Similarity measures the cosine of the angle between two non-zero 
multidimensional vectors in an inner product space.
Formula:
    Cosine Similarity(A, B) = (A · B) / (||A|| × ||B||)
where:
    - (A · B) is the dot product: sum(A_i * B_i) for all products i.
    - ||A|| is the Euclidean magnitude of vector A: sqrt(sum(A_i^2)).
    - ||B|| is the Euclidean magnitude of vector B: sqrt(sum(B_i^2)).
    - Range: [0.0, 1.0] for non-negative purchase quantity vectors.

WHY WE NEED IT IN SHOPLYTICS:
1. Behavioral Affinity & Collaborative Filtering: Finds customers with similar 
   purchasing intensity and item preferences.
2. Magnitude-Invariant Basket Comparison: Evaluates orientation rather than raw 
   scale (e.g., a customer who bought 2 items of P1 and 1 of P2 has high similarity 
   with one who bought 4 of P1 and 2 of P2).
3. Personalized Recommendations: Powers customer-to-customer lookalike discovery.

BIG DATA SCALABILITY (INVERTED INDEX CANDIDATE GENERATION):
Comparing 95,420 customers blindly (O(N^2)) requires calculating 4,552,440,490 
(4.55 BILLION) pairwise comparisons.
Instead, we construct an Inverted Index (Product -> Customers) to generate candidate 
pairs ONLY for customers sharing at least one product, pruning >99.96% of 
unnecessary computations and completing in seconds.

WHERE IT FITS:
Orders + Items Data -> Sparse Vectors -> Inverted Index -> Cosine Engine -> HDFS / Dashboard
==============================================================================
"""

import os
import sys
import time
import math
from datetime import datetime
from collections import defaultdict
import pandas as pd
import numpy as np


class CosineSimilarityEngine:
    """
    Scalable, sparse Cosine Similarity Engine for e-commerce customer purchase vectors.
    Avoids dense matrix memory bottlenecks and uses inverted index candidate pairing.
    """

    def __init__(self):
        self.customer_vectors = defaultdict(dict)  # {cust_id: {prod_id: quantity}}
        self.magnitudes = {}  # {cust_id: float}
        self.purchase_counts = {}  # {cust_id: int}
        self.inverted_index = defaultdict(list)  # {prod_id: [cust_ids]}
        self.total_customers = 0
        self.total_unique_products = 0
        self.candidate_pairs_count = 0
        self.similar_pairs = []  # list of tuples: (c1, c2, cosine, common_prods, count_c1, count_c2)
        self.stats = {}

    @staticmethod
    def compute_cosine_vector_pair(vec_a: dict, vec_b: dict) -> float:
        """
        Computes cosine similarity between two sparse dictionary vectors.
        Used for validation and standalone pair comparison.
        """
        if not vec_a or not vec_b:
            return 0.0
        
        # Shared keys dot product
        common_keys = set(vec_a.keys()) & set(vec_b.keys())
        if not common_keys:
            return 0.0

        dot_product = sum(vec_a[k] * vec_b[k] for k in common_keys)
        mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
        mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

        if mag_a == 0.0 or mag_b == 0.0:
            return 0.0

        return dot_product / (mag_a * mag_b)

    def run_validation_test(self):
        """
        Executes built-in unit validation tests to verify mathematical correctness.
        """
        print("\n==========================================")
        print("RUNNING VALIDATION TESTS")
        print("==========================================")
        
        # Test Case 1: Standard example from specification:
        # A = [1, 0, 1] (P1: 1, P3: 1)
        # B = [1, 1, 0] (P1: 1, P2: 1)
        # Dot = 1*1 = 1, ||A|| = sqrt(2), ||B|| = sqrt(2) -> Cosine = 1 / 2 = 0.5
        vec_a = {"P1": 1, "P3": 1}
        vec_b = {"P1": 1, "P2": 1}
        sim1 = self.compute_cosine_vector_pair(vec_a, vec_b)
        expected1 = 0.5
        assert math.isclose(sim1, expected1, rel_tol=1e-5), f"Test 1 Failed: {sim1} != {expected1}"
        print(f"Test 1 (Specification Example): A=[1,0,1], B=[1,1,0]")
        print(f"  -> Calculated: {sim1:.4f} | Expected: {expected1:.4f} [PASSED]")

        # Test Case 2: Multi-quantity proportional vectors:
        # A = [2, 1, 4] -> mag = sqrt(4 + 1 + 16) = sqrt(21)
        # B = [1, 1, 2] -> mag = sqrt(1 + 1 + 4) = sqrt(6)
        # Dot = 2*1 + 1*1 + 4*2 = 2 + 1 + 8 = 11
        # Cosine = 11 / (sqrt(21) * sqrt(6)) = 11 / sqrt(126) ≈ 0.9800
        vec_a2 = {"P1": 2, "P2": 1, "P3": 4}
        vec_b2 = {"P1": 1, "P2": 1, "P3": 2}
        sim2 = self.compute_cosine_vector_pair(vec_a2, vec_b2)
        expected2 = 11.0 / math.sqrt(126.0)
        assert math.isclose(sim2, expected2, rel_tol=1e-5), f"Test 2 Failed: {sim2} != {expected2}"
        print(f"Test 2 (Multi-quantity Vectors): A=[2,1,4], B=[1,1,2]")
        print(f"  -> Calculated: {sim2:.4f} | Expected: {expected2:.4f} [PASSED]")

        # Test Case 3: Disjoint vectors (Orthogonal)
        vec_a3 = {"P1": 2}
        vec_b3 = {"P2": 3}
        sim3 = self.compute_cosine_vector_pair(vec_a3, vec_b3)
        assert sim3 == 0.0, f"Test 3 Failed: {sim3} != 0.0"
        print(f"Test 3 (Orthogonal Vectors): A=[P1:2], B=[P2:3]")
        print(f"  -> Calculated: {sim3:.4f} | Expected: 0.0000 [PASSED]")

        # Test Case 4: Identical directions (Collinear)
        vec_a4 = {"P1": 1, "P2": 2}
        vec_b4 = {"P1": 2, "P2": 4}
        sim4 = self.compute_cosine_vector_pair(vec_a4, vec_b4)
        assert math.isclose(sim4, 1.0, rel_tol=1e-5), f"Test 4 Failed: {sim4} != 1.0"
        print(f"Test 4 (Collinear Vectors): A=[1,2], B=[2,4]")
        print(f"  -> Calculated: {sim4:.4f} | Expected: 1.0000 [PASSED]")

        print("All validation tests passed successfully!\n")

    def build_customer_vectors(self, df_merged: pd.DataFrame, customer_col: str = "customer_unique_id", product_col: str = "product_id"):
        """
        Builds sparse customer-product purchase quantity vectors and inverted index.
        Applies strict error handling and data cleaning.
        """
        print("[STEP 2] Cleaning and sanitizing transaction records...")
        # Handle missing, null, or malformed fields
        df_clean = df_merged.dropna(subset=[customer_col, product_col]).copy()
        df_clean[customer_col] = df_clean[customer_col].astype(str).str.strip()
        df_clean[product_col] = df_clean[product_col].astype(str).str.strip()
        df_clean = df_clean[(df_clean[customer_col] != "") & (df_clean[product_col] != "")]

        print(f"Sanitized rows for vectorization: {len(df_clean):,}")

        print("[STEP 3] Aggregating purchase quantities per customer-product pair...")
        grouped = df_clean.groupby([customer_col, product_col]).size()

        print("[STEP 4] Constructing sparse vectors, magnitudes, and inverted index...")
        for (cust, prod), qty in grouped.items():
            if qty > 0:
                self.customer_vectors[cust][prod] = int(qty)
                self.inverted_index[prod].append(cust)

        self.total_customers = len(self.customer_vectors)
        self.total_unique_products = len(self.inverted_index)

        # Precalculate vector magnitudes and total purchase counts
        for cust, vec in self.customer_vectors.items():
            self.magnitudes[cust] = math.sqrt(sum(q * q for q in vec.values()))
            self.purchase_counts[cust] = sum(vec.values())

        print(f"Customers vectorized: {self.total_customers:,}")
        print(f"Unique products indexed: {self.total_unique_products:,}")

    def compute_similarity(self):
        """
        Computes exact cosine similarity across all candidate pairs sharing at least one product.
        Prunes O(N^2) search space via inverted index.
        """
        print("\n[STEP 5] Generating candidate pairs and accumulating dot products...")
        t0 = time.perf_counter()

        # pair_accumulator: (c1, c2) -> [dot_product, common_products_count]
        # Lexicographical ordering c1 < c2 ensures symmetric uniqueness (A, B) == (B, A)
        pair_accumulator = defaultdict(lambda: [0, 0])

        for prod, cust_list in self.inverted_index.items():
            n = len(cust_list)
            if n >= 2:
                sorted_custs = sorted(cust_list)
                for i in range(n):
                    c1 = sorted_custs[i]
                    q1 = self.customer_vectors[c1][prod]
                    for j in range(i + 1, n):
                        c2 = sorted_custs[j]
                        q2 = self.customer_vectors[c2][prod]
                        rec = pair_accumulator[(c1, c2)]
                        rec[0] += q1 * q2
                        rec[1] += 1

        self.candidate_pairs_count = len(pair_accumulator)
        pair_gen_time = time.perf_counter() - t0
        print(f"Candidate pairs evaluated: {self.candidate_pairs_count:,} (in {pair_gen_time:.2f}s)")

        print("[STEP 6] Calculating final cosine similarity and ranking top pairs...")
        results = []
        for (c1, c2), (dot, common_cnt) in pair_accumulator.items():
            mag1 = self.magnitudes[c1]
            mag2 = self.magnitudes[c2]
            if mag1 > 0 and mag2 > 0:
                cosine = dot / (mag1 * mag2)
                # Clamp minor floating point inaccuracies to 1.0
                if cosine > 1.0:
                    cosine = 1.0
                if cosine > 0:
                    results.append((
                        c1,
                        c2,
                        round(cosine, 6),
                        common_cnt,
                        self.purchase_counts[c1],
                        self.purchase_counts[c2]
                    ))

        # Sort results: descending by cosine similarity, then common products count, then total purchase counts
        results.sort(key=lambda x: (x[2], x[3], x[4] + x[5]), reverse=True)
        self.similar_pairs = results

        # Global metrics
        total_possible_pairs = (self.total_customers * (self.total_customers - 1)) // 2
        pruning_ratio = ((total_possible_pairs - self.candidate_pairs_count) / total_possible_pairs) * 100 if total_possible_pairs > 0 else 0.0
        cosine_values = [r[2] for r in self.similar_pairs]

        max_sim = max(cosine_values) if cosine_values else 0.0
        avg_sim = sum(cosine_values) / len(cosine_values) if cosine_values else 0.0

        self.stats = {
            "customers_analyzed": self.total_customers,
            "unique_products": self.total_unique_products,
            "total_possible_pairs": total_possible_pairs,
            "candidate_pairs": self.candidate_pairs_count,
            "similar_pairs": len(self.similar_pairs),
            "candidate_pruning_ratio_percent": round(pruning_ratio, 4),
            "maximum_similarity": round(max_sim, 4),
            "average_similarity": round(avg_sim, 4)
        }


# ==============================================================================
# MAIN EXECUTION & BENCHMARKING PIPELINE
# ==============================================================================

def main():
    print("==========================================")
    print("  SHOPLYTICS: COSINE SIMILARITY ENGINE    ")
    print("==========================================")

    start_datetime = datetime.now()
    start_time = time.perf_counter()
    print(f"Execution Start Time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Instantiate Engine and Run Built-in Validation Tests
    engine = CosineSimilarityEngine()
    engine.run_validation_test()

    # 2. Load E-Commerce Data
    order_items_file = r"C:\Projects\Shoplytics\data\processed\order_items_clean.csv"
    orders_file = r"C:\Projects\Shoplytics\data\processed\orders_clean.csv"
    customers_file = r"C:\Projects\Shoplytics\data\processed\customers_clean.csv"

    print("[STEP 1] Loading Olist Brazilian E-Commerce Data...")
    if not os.path.exists(order_items_file):
        print(f"Error: Missing required input file {order_items_file}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(orders_file):
        print(f"Error: Missing required input file {orders_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading order items : {order_items_file}")
    df_items = pd.read_csv(order_items_file)
    print(f"Loading orders      : {orders_file}")
    df_orders = pd.read_csv(orders_file)

    # Merge items with orders to get customer_id
    df_merged = df_items.merge(df_orders[["order_id", "customer_id"]], on="order_id", how="inner")

    # If customers_clean.csv is present, map to customer_unique_id for true cross-order customer tracking
    customer_col = "customer_id"
    if os.path.exists(customers_file):
        print(f"Loading customers   : {customers_file} (mapping to unique customer entities)")
        df_customers = pd.read_csv(customers_file)
        if "customer_unique_id" in df_customers.columns and "customer_id" in df_customers.columns:
            df_merged = df_merged.merge(df_customers[["customer_id", "customer_unique_id"]], on="customer_id", how="inner")
            customer_col = "customer_unique_id"

    print(f"Total merged transaction items: {len(df_merged):,}")

    # 3. Vectorize and Compute Similarities
    engine.build_customer_vectors(df_merged, customer_col=customer_col, product_col="product_id")
    engine.compute_similarity()

    end_time = time.perf_counter()
    end_datetime = datetime.now()
    execution_time_sec = end_time - start_time

    # 4. Display Results Summary according to specification
    print("\n==========================================")
    print("COSINE SIMILARITY RESULTS")
    print("==========================================")
    print(f"Customers analyzed       : {engine.stats['customers_analyzed']:,}")
    print(f"Unique products          : {engine.stats['unique_products']:,}")
    print(f"Candidate pairs          : {engine.stats['candidate_pairs']:,}")
    print(f"Similar pairs            : {engine.stats['similar_pairs']:,}")
    print(f"Maximum similarity       : {engine.stats['maximum_similarity']:.4f}")
    print(f"Average similarity       : {engine.stats['average_similarity']:.4f}")
    print(f"Execution time           : {execution_time_sec:.2f} seconds")

    # 5. Display Top Similar Customer Pairs
    print("\n==========================================")
    print("TOP SIMILAR CUSTOMER PAIRS")
    print("==========================================")
    print(f"{'Customer A':<34} {'Customer B':<34} {'Cosine Similarity':<18} {'Common':<8} {'Qty A':<6} {'Qty B':<6}")
    print("-" * 112)

    for c1, c2, sim, common_cnt, cnt1, cnt2 in engine.similar_pairs[:15]:
        print(f"{c1:<34} {c2:<34} {sim:<18.4f} {common_cnt:<8} {cnt1:<6} {cnt2:<6}")

    # 6. Save Results Locally
    output_dir = r"C:\Projects\Shoplytics\results\cosine"
    os.makedirs(output_dir, exist_ok=True)

    # 6.1 cosine_summary.csv
    summary_file = os.path.join(output_dir, "cosine_summary.csv")
    df_summary = pd.DataFrame([{
        "customers_analyzed": engine.stats["customers_analyzed"],
        "unique_products": engine.stats["unique_products"],
        "total_possible_pairs": engine.stats["total_possible_pairs"],
        "candidate_pairs": engine.stats["candidate_pairs"],
        "similar_pairs": engine.stats["similar_pairs"],
        "candidate_pruning_ratio_percent": engine.stats["candidate_pruning_ratio_percent"],
        "maximum_similarity": engine.stats["maximum_similarity"],
        "average_similarity": engine.stats["average_similarity"],
        "start_time": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "execution_time_seconds": round(execution_time_sec, 2)
    }])
    df_summary.to_csv(summary_file, index=False)

    # 6.2 top_cosine_pairs.csv (Top 1,000 most similar pairs)
    top_pairs_file = os.path.join(output_dir, "top_cosine_pairs.csv")
    df_top = pd.DataFrame(engine.similar_pairs[:1000], columns=[
        "customer_id", "similar_customer_id", "cosine_similarity", "common_products",
        "customer_purchase_count", "similar_customer_purchase_count"
    ])
    df_top.to_csv(top_pairs_file, index=False)

    # 6.3 cosine_results.csv (Top 10,000 representative similar pairs for downstream engine & dashboard)
    results_file = os.path.join(output_dir, "cosine_results.csv")
    df_results = pd.DataFrame(engine.similar_pairs[:10000], columns=[
        "customer_id", "similar_customer_id", "cosine_similarity", "common_products",
        "customer_purchase_count", "similar_customer_purchase_count"
    ])
    df_results.to_csv(results_file, index=False)

    print("\n==========================================")
    print("COSINE RESULT FILES SAVED LOCALLY")
    print("==========================================")
    print(f"1. Summary File     : {summary_file}")
    print(f"2. Top Pairs File   : {top_pairs_file} (Top 1,000 pairs)")
    print(f"3. Results Sample   : {results_file} (Top 10,000 pairs)")
    print("\n==========================================")
    print("COSINE EXECUTION COMPLETED SUCCESSFULLY")
    print("==========================================")


if __name__ == "__main__":
    main()

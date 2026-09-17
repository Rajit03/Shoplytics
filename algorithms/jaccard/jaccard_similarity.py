"""
==============================================================================
SHOPLYTICS: Distributed Big Data Analytics Platform for E-Commerce
ALGORITHM: Jaccard Similarity (Customer-to-Customer Product Set Similarity)
==============================================================================

WHAT IT DOES:
Jaccard Similarity measures the similarity between two finite sample sets (A and B).
Formula:
    J(A, B) = |A ∩ B| / |A ∪ B|
where:
    - |A ∩ B| is the intersection count (products purchased by BOTH Customer A and B).
    - |A ∪ B| is the union count (total distinct products purchased across BOTH).
    - Range: 0.0 (completely disjoint sets) to 1.0 (identical product sets).

WHY WE NEED IT IN SHOPLYTICS:
1. Collaborative Filtering: "Customers with similar tastes also bought...".
2. Customer Segmentation Validation: Validates behavioral clustering (K-Means).
3. Targeted Marketing & Personalization: Identifies customer lookalikes for retargeting campaigns.

BIG DATA SCALABILITY (CANDIDATE GENERATION VIA INVERTED INDEX):
Comparing 95,420 customers blindly (O(N^2)) requires calculating 4,552,476,090 
(4.55 BILLION) pairwise comparisons.
Instead, we build an Inverted Index (Product -> Customers). Candidate pairs are 
generated ONLY for customers who share at least one product, pruning >99.96% of 
irrelevant pairs and executing in seconds.

WHERE IT FITS:
Transactions / Orders Data -> Inverted Index -> Jaccard Engine -> Recommendation / HDFS
==============================================================================
"""

import os
import sys
import time
from datetime import datetime
from collections import defaultdict
from itertools import combinations
import pandas as pd
import numpy as np


class JaccardSimilarityEngine:
    """
    Scalable Jaccard Similarity Engine for large e-commerce customer bases.
    Implements inverted index candidate generation to avoid O(N^2) pairwise brute force.
    """

    def __init__(self):
        self.customer_product_sets = {}  # {customer_id: set(product_ids)}
        self.inverted_index = defaultdict(list)  # {product_id: [customer_ids]}
        self.total_customers = 0
        self.total_unique_products = 0
        self.candidate_pairs_count = 0
        self.similar_pairs = []  # list of tuples (c1, c2, inter, union, jaccard)
        self.stats = {}

    def fit(self, df_transactions: pd.DataFrame, customer_col: str = "customer_unique_id", product_col: str = "product_id"):
        """
        Builds customer product profiles, inverted index, and calculates exact Jaccard similarity.
        """
        # 1. Clean and deduplicate input data
        df_clean = df_transactions.dropna(subset=[customer_col, product_col]).copy()
        df_clean[customer_col] = df_clean[customer_col].astype(str).str.strip()
        df_clean[product_col] = df_clean[product_col].astype(str).str.strip()
        df_clean = df_clean[(df_clean[customer_col] != "") & (df_clean[product_col] != "")]

        # 2. Build Customer -> Product Sets
        print("\n[STEP 2] Building Customer-Product Baskets...")
        grouped = df_clean.groupby(customer_col)[product_col].unique()
        self.customer_product_sets = {cust: set(prods) for cust, prods in grouped.items() if len(prods) > 0}
        self.total_customers = len(self.customer_product_sets)

        # 3. Build Inverted Index (Product -> Customers)
        print("[STEP 3] Constructing Inverted Index (Product -> Customers)...")
        for cust, prods in self.customer_product_sets.items():
            for p in prods:
                self.inverted_index[p].append(cust)
        self.total_unique_products = len(self.inverted_index)

        # 4. Generate Candidate Pairs (Pairs sharing >= 1 product)
        print("[STEP 4] Generating Candidate Customer Pairs via Inverted Index...")
        candidate_pair_set = set()
        for prod, cust_list in self.inverted_index.items():
            if len(cust_list) >= 2:
                # Lexicographically sort to ensure (A, B) is stored and (B, A) duplicate is avoided
                sorted_custs = sorted(cust_list)
                for c1, c2 in combinations(sorted_custs, 2):
                    candidate_pair_set.add((c1, c2))

        self.candidate_pairs_count = len(candidate_pair_set)

        # 5. Calculate Exact Jaccard Similarity on Candidates
        print(f"[STEP 5] Computing Exact Jaccard Similarity on {self.candidate_pairs_count:,} Candidate Pairs...")
        results = []
        for c1, c2 in candidate_pair_set:
            s1 = self.customer_product_sets[c1]
            s2 = self.customer_product_sets[c2]
            inter_count = len(s1 & s2)
            union_count = len(s1 | s2)
            jaccard = inter_count / union_count
            if jaccard > 0:
                results.append((c1, c2, inter_count, union_count, round(jaccard, 6)))

        # Sort results: highest similarity first, then largest intersection count
        results.sort(key=lambda x: (x[4], x[2]), reverse=True)
        self.similar_pairs = results

        # 6. Compute Global Metrics
        total_possible_pairs = (self.total_customers * (self.total_customers - 1)) // 2
        pruning_ratio = ((total_possible_pairs - self.candidate_pairs_count) / total_possible_pairs) * 100
        jaccard_values = [r[4] for r in self.similar_pairs]

        max_sim = max(jaccard_values) if jaccard_values else 0.0
        avg_sim = statistics_mean = sum(jaccard_values) / len(jaccard_values) if jaccard_values else 0.0

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
    print("   SHOPLYTICS: JACCARD SIMILARITY ENGINE  ")
    print("==========================================")

    start_datetime = datetime.now()
    start_time = time.perf_counter()
    print(f"Execution Start Time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Load Dataset
    transactions_file = r"C:\Projects\Shoplytics\data\processed\transactions.csv"
    order_items_file = r"C:\Projects\Shoplytics\data\processed\order_items_clean.csv"
    orders_file = r"C:\Projects\Shoplytics\data\processed\orders_clean.csv"

    print("\n[STEP 1] Loading E-Commerce Transaction Data...")
    if os.path.exists(transactions_file):
        print(f"Loading transactions file: {transactions_file}")
        df = pd.read_csv(transactions_file)
        customer_col = "customer_unique_id"
        product_col = "product_id"
    else:
        print(f"Falling back to order_items + orders merge...")
        df_items = pd.read_csv(order_items_file)
        df_orders = pd.read_csv(orders_file)
        df = df_items.merge(df_orders[["order_id", "customer_id"]], on="order_id", how="inner")
        customer_col = "customer_id"
        product_col = "product_id"

    print(f"Total raw transaction rows: {len(df):,}")

    # 2. Run Jaccard Engine
    engine = JaccardSimilarityEngine()
    engine.fit(df, customer_col=customer_col, product_col=product_col)

    end_time = time.perf_counter()
    end_datetime = datetime.now()
    execution_time_sec = end_time - start_time

    # 3. Print Results Summary
    print("\n==========================================")
    print("JACCARD SIMILARITY RESULTS")
    print("==========================================")
    print(f"Customers analyzed       : {engine.stats['customers_analyzed']:,}")
    print(f"Unique products          : {engine.stats['unique_products']:,}")
    print(f"Total possible pairs     : {engine.stats['total_possible_pairs']:,} (4.55 Billion)")
    print(f"Candidate pairs          : {engine.stats['candidate_pairs']:,}")
    print(f"Similar pairs (J > 0)    : {engine.stats['similar_pairs']:,}")
    print(f"Candidate Pruning Ratio  : {engine.stats['candidate_pruning_ratio_percent']:.4f} % (Pairs avoided)")
    print(f"Maximum similarity       : {engine.stats['maximum_similarity']:.4f}")
    print(f"Average similarity       : {engine.stats['average_similarity']:.4f}")
    print(f"Execution time           : {execution_time_sec:.2f} seconds")

    # 4. Display Top Similar Customer Pairs
    print("\n==========================================")
    print("TOP SIMILAR CUSTOMER PAIRS")
    print("==========================================")
    print(f"{'Customer A':<34} {'Customer B':<34} {'Inter':<6} {'Union':<6} {'Jaccard':<8}")
    print("-" * 92)

    for c1, c2, inter, union, sim in engine.similar_pairs[:15]:
        print(f"{c1:<34} {c2:<34} {inter:<6} {union:<6} {sim:<8.4f}")

    # 5. Save Results Locally
    output_dir = r"C:\Projects\Shoplytics\results\jaccard"
    os.makedirs(output_dir, exist_ok=True)

    # 5.1 jaccard_summary.csv
    summary_file = os.path.join(output_dir, "jaccard_summary.csv")
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

    # 5.2 top_jaccard_pairs.csv (Top 1,000 most similar pairs)
    top_pairs_file = os.path.join(output_dir, "top_jaccard_pairs.csv")
    df_top = pd.DataFrame(engine.similar_pairs[:1000], columns=[
        "customer_id", "similar_customer_id", "intersection_count", "union_count", "jaccard_similarity"
    ])
    df_top.to_csv(top_pairs_file, index=False)

    # 5.3 jaccard_results.csv (Top 10,000 representative similar pairs for storage/dashboard)
    results_file = os.path.join(output_dir, "jaccard_results.csv")
    df_results = pd.DataFrame(engine.similar_pairs[:10000], columns=[
        "customer_id", "similar_customer_id", "intersection_count", "union_count", "jaccard_similarity"
    ])
    df_results.to_csv(results_file, index=False)

    print("\n==========================================")
    print("JACCARD RESULT FILES SAVED LOCALLY")
    print("==========================================")
    print(f"1. Summary File     : {summary_file}")
    print(f"2. Top Pairs File   : {top_pairs_file} (Top 1,000 pairs)")
    print(f"3. Results Sample   : {results_file} (Top 10,000 pairs)")
    print("\n==========================================")
    print("JACCARD EXECUTION COMPLETED SUCCESSFULLY")
    print("==========================================")


if __name__ == "__main__":
    main()

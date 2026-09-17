"""
==============================================================================
SHOPLYTICS: Distributed Big Data Analytics Platform for E-Commerce
MODULE: Hybrid Recommendation Engine
==============================================================================

WHAT IT DOES:
The Shoplytics Recommendation Engine delivers personalized product recommendations 
by combining multiple Big Data analytics and machine learning signals:
1. Apriori Association Rules: Mining frequent itemsets and co-purchase affinities
   (confidence & lift).
2. Collaborative Filtering via Similarity: Recommending products purchased by 
   behaviorally aligned customers discovered through Cosine & Jaccard similarity.
3. Product Popularity & Category Baseline: Resolving cold-start and sparse candidate 
   pools via normalized global catalog purchase frequencies.

HYBRID SCORING FORMULA:
For a candidate product p not previously purchased by customer C (p ∉ History(C)):
    Score(p) = w_apriori * S_apriori(p) + w_sim * S_sim(p) + w_pop * S_pop(p)
where:
    - S_apriori(p) = max_{Antecedent ⊆ History(C), p ∈ Consequent} (Confidence * min(1.0, Lift / 50.0))
    - S_sim(p) = sum_{C' ∈ Neighbors(C), p ∈ History(C')} Sim(C, C') / sum_{C' ∈ Neighbors(C)} Sim(C, C')
    - S_pop(p) = Frequency(p) / MaxFrequency
    - Default weights: w_apriori = 0.45, w_sim = 0.40, w_pop = 0.15 (or Popularity = 1.0 for fallback candidates)

EXCLUSION GUARANTEE:
Under no circumstances are products that customer C has already purchased returned.

WHERE IT FITS:
Preprocessing + Big Data Algorithms (Apriori, Cosine, Jaccard) 
-> Recommendation Engine -> NoSQL Database -> FastAPI -> React Dashboard
==============================================================================
"""

import os
import sys
import time
import argparse
from datetime import datetime
from collections import defaultdict
import pandas as pd
import numpy as np


class ShoplyticsRecommendationEngine:
    """
    Production-grade Hybrid Recommendation Engine integrating Apriori Association Rules,
    Collaborative Customer Similarity (Cosine/Jaccard), and Catalog Popularity.
    """

    def __init__(self,
                 w_apriori: float = 0.45,
                 w_similarity: float = 0.40,
                 w_popularity: float = 0.15):
        self.w_apriori = w_apriori
        self.w_similarity = w_similarity
        self.w_popularity = w_popularity

        # In-memory structures
        self.customer_history = defaultdict(set)       # {cust_id: set(prod_ids)}
        self.product_popularity = defaultdict(int)     # {prod_id: count}
        self.max_popularity = 1
        self.top_popular_products = []                 # [(prod_id, pop_score), ...]
        
        self.product_categories = {}                   # {prod_id: category_name}
        self.rules = []                                # [(antecedent_set, consequent_set, conf, lift, support)]
        self.similarity_graph = defaultdict(dict)      # {cust_id: {sim_cust_id: max_sim_score}}
        
        self.total_customers = 0
        self.total_products = 0
        self.total_rules = 0
        self.total_similarity_pairs = 0

    def load_data(self,
                  data_dir: str = r"C:\Projects\Shoplytics\data\processed",
                  results_dir: str = r"C:\Projects\Shoplytics\results"):
        """
        Loads all required datasets, prior algorithm outputs, and product metadata.
        """
        print("\n[STEP 1] Loading Base E-Commerce Data & Customer Purchase Histories...")
        order_items_file = os.path.join(data_dir, "order_items_clean.csv")
        orders_file = os.path.join(data_dir, "orders_clean.csv")
        customers_file = os.path.join(data_dir, "customers_clean.csv")
        products_file = os.path.join(data_dir, "products_clean.csv")

        # 1. Load Order Items & Orders
        df_items = pd.read_csv(order_items_file)
        df_orders = pd.read_csv(orders_file)
        df_merged = df_items.merge(df_orders[["order_id", "customer_id"]], on="order_id", how="inner")

        # Map to customer_unique_id if customers_clean is available
        customer_col = "customer_id"
        if os.path.exists(customers_file):
            df_cust = pd.read_csv(customers_file)
            if "customer_unique_id" in df_cust.columns and "customer_id" in df_cust.columns:
                df_merged = df_merged.merge(df_cust[["customer_id", "customer_unique_id"]], on="customer_id", how="inner")
                customer_col = "customer_unique_id"

        # Build customer history and product popularity
        df_clean = df_merged.dropna(subset=[customer_col, "product_id"])
        grouped = df_clean.groupby(customer_col)["product_id"].unique()
        for cust_id, prods in grouped.items():
            cust_str = str(cust_id).strip()
            if cust_str:
                self.customer_history[cust_str] = set(str(p).strip() for p in prods if str(p).strip())

        pop_counts = df_clean["product_id"].value_counts()
        for p_id, count in pop_counts.items():
            p_str = str(p_id).strip()
            if p_str:
                self.product_popularity[p_str] = int(count)

        self.max_popularity = max(self.product_popularity.values()) if self.product_popularity else 1
        self.total_customers = len(self.customer_history)
        self.total_products = len(self.product_popularity)

        # Ranked list of popular products: (prod_id, normalized_popularity_score)
        self.top_popular_products = [
            (p, count / self.max_popularity)
            for p, count in pop_counts.items()
        ]

        print(f"Loaded {self.total_customers:,} active customer profiles and {self.total_products:,} unique products.")

        # 2. Load Product Categories
        if os.path.exists(products_file):
            print(f"[STEP 2] Loading Product Metadata & Category Taxonomy from {products_file}...")
            df_prod = pd.read_csv(products_file)
            cat_col = "product_category_name_english" if "product_category_name_english" in df_prod.columns else "product_category_name"
            if cat_col in df_prod.columns and "product_id" in df_prod.columns:
                for _, row in df_prod.iterrows():
                    p_id = str(row["product_id"]).strip()
                    cat = str(row[cat_col]).strip() if pd.notna(row[cat_col]) else "general"
                    self.product_categories[p_id] = cat
            print(f"Indexed {len(self.product_categories):,} product category mappings.")
        else:
            print("[STEP 2] Product category file not found. Defaulting category mappings to 'general'.")

        # 3. Load Apriori Association Rules
        apriori_file = os.path.join(results_dir, "apriori", "association_rules.csv")
        if os.path.exists(apriori_file):
            print(f"[STEP 3] Loading Apriori Association Rules from {apriori_file}...")
            df_rules = pd.read_csv(apriori_file)
            for _, row in df_rules.iterrows():
                try:
                    ants = set(str(row["antecedent"]).split(";"))
                    cons = set(str(row["consequent"]).split(";"))
                    conf = float(row.get("confidence", 0.0))
                    lift = float(row.get("lift", 1.0))
                    supp = float(row.get("support", 0.0))
                    self.rules.append((ants, cons, conf, lift, supp))
                except Exception:
                    continue
            self.total_rules = len(self.rules)
            print(f"Loaded {self.total_rules:,} association rules.")
        else:
            print("[STEP 3] Warning: Apriori association rules file not found. Apriori channel skipped.")

        # 4. Load Customer Similarity Results (Cosine + Jaccard)
        cosine_file = os.path.join(results_dir, "cosine", "cosine_results.csv")
        jaccard_file = os.path.join(results_dir, "jaccard", "jaccard_results.csv")

        print("[STEP 4] Loading Collaborative Similarity Graphs (Cosine & Jaccard)...")
        pairs_loaded = 0

        # Cosine Similarity
        if os.path.exists(cosine_file):
            df_cos = pd.read_csv(cosine_file)
            for _, row in df_cos.iterrows():
                try:
                    c1 = str(row["customer_id"]).strip()
                    c2 = str(row["similar_customer_id"]).strip()
                    sim = float(row["cosine_similarity"])
                    if sim > 0:
                        self.similarity_graph[c1][c2] = max(self.similarity_graph[c1].get(c2, 0.0), sim)
                        self.similarity_graph[c2][c1] = max(self.similarity_graph[c2].get(c1, 0.0), sim)
                        pairs_loaded += 1
                except Exception:
                    continue

        # Jaccard Similarity (Complementary)
        if os.path.exists(jaccard_file):
            df_jac = pd.read_csv(jaccard_file)
            for _, row in df_jac.iterrows():
                try:
                    c1 = str(row["customer_id"]).strip()
                    c2 = str(row["similar_customer_id"]).strip()
                    sim = float(row["jaccard_similarity"])
                    if sim > 0:
                        self.similarity_graph[c1][c2] = max(self.similarity_graph[c1].get(c2, 0.0), sim)
                        self.similarity_graph[c2][c1] = max(self.similarity_graph[c2].get(c1, 0.0), sim)
                        pairs_loaded += 1
                except Exception:
                    continue

        self.total_similarity_pairs = pairs_loaded
        print(f"Constructed similarity graph for {len(self.similarity_graph):,} customers with {pairs_loaded:,} relationship edges.")

    def recommend(self, customer_id: str, top_n: int = 10) -> list:
        """
        Generates Top-N product recommendations for a single customer.
        Returns list of dicts with ranked recommendations and attribution metrics.
        """
        customer_id = str(customer_id).strip()
        history = self.customer_history.get(customer_id, set())

        # Candidate stores: prod_id -> score components
        apriori_candidates = defaultdict(float)    # prod_id -> apriori_score
        similarity_candidates = defaultdict(float) # prod_id -> similarity_score
        
        # -------------------------------------------------------------
        # CHANNEL 1: Apriori Association Rules
        # -------------------------------------------------------------
        if history and self.rules:
            for ants, cons, conf, lift, _ in self.rules:
                if ants.issubset(history):
                    # Products in consequent not already bought
                    for p in cons:
                        if p not in history:
                            # Score bounded [0, 1] using confidence and normalized lift
                            lift_factor = min(1.0, lift / 50.0) if lift > 0 else 0.5
                            rule_score = conf * lift_factor
                            if rule_score > apriori_candidates[p]:
                                apriori_candidates[p] = rule_score

        # -------------------------------------------------------------
        # CHANNEL 2: Collaborative Filtering (Similar Customers)
        # -------------------------------------------------------------
        if customer_id in self.similarity_graph:
            neighbors = self.similarity_graph[customer_id]
            sum_sim_weights = sum(neighbors.values())
            if sum_sim_weights > 0:
                for sim_cust, sim_val in neighbors.items():
                    sim_cust_history = self.customer_history.get(sim_cust, set())
                    for p in sim_cust_history:
                        if p not in history:
                            # Weighted affinity
                            similarity_candidates[p] += (sim_val / sum_sim_weights)

                # Normalize similarity candidate scores to [0, 1]
                if similarity_candidates:
                    max_sim_cand = max(similarity_candidates.values())
                    if max_sim_cand > 0:
                        for p in similarity_candidates:
                            similarity_candidates[p] = similarity_candidates[p] / max_sim_cand

        # -------------------------------------------------------------
        # CHANNEL 3: Aggregate Candidates & Calculate Hybrid Score
        # -------------------------------------------------------------
        all_candidate_prods = set(apriori_candidates.keys()) | set(similarity_candidates.keys())
        ranked_candidates = []

        for p in all_candidate_prods:
            s_ap = apriori_candidates.get(p, 0.0)
            s_sim = similarity_candidates.get(p, 0.0)
            s_pop = self.product_popularity.get(p, 0) / self.max_popularity

            # Determine attribution source
            if s_ap > 0 and s_sim > 0:
                source = "Hybrid (Apriori + Similar Customers)"
                final_score = (self.w_apriori * s_ap) + (self.w_similarity * s_sim) + (self.w_popularity * s_pop)
            elif s_ap > 0:
                source = "Apriori Association Rules"
                final_score = (0.75 * s_ap) + (0.25 * s_pop)
            else:
                source = "Collaborative Filtering (Similar Customers)"
                final_score = (0.75 * s_sim) + (0.25 * s_pop)

            ranked_candidates.append({
                "product_id": p,
                "product_category": self.product_categories.get(p, "general"),
                "recommendation_score": round(final_score, 4),
                "apriori_score": round(s_ap, 4),
                "similarity_score": round(s_sim, 4),
                "popularity_score": round(s_pop, 4),
                "recommendation_source": source
            })

        # Sort candidates descending by recommendation_score, then popularity
        ranked_candidates.sort(key=lambda x: (x["recommendation_score"], x["popularity_score"]), reverse=True)

        # -------------------------------------------------------------
        # CHANNEL 4: Popularity Fallback for Cold-Start / Insufficient Candidates
        # -------------------------------------------------------------
        if len(ranked_candidates) < top_n:
            seen_prods = history | {c["product_id"] for c in ranked_candidates}
            for p, pop_score in self.top_popular_products:
                if p not in seen_prods:
                    ranked_candidates.append({
                        "product_id": p,
                        "product_category": self.product_categories.get(p, "general"),
                        "recommendation_score": round(pop_score, 4),
                        "apriori_score": 0.0,
                        "similarity_score": 0.0,
                        "popularity_score": round(pop_score, 4),
                        "recommendation_source": "Popularity Fallback"
                    })
                    seen_prods.add(p)
                    if len(ranked_candidates) >= top_n:
                        break

        # Assign ranks
        final_recommendations = ranked_candidates[:top_n]
        for idx, item in enumerate(final_recommendations, start=1):
            item["rank"] = idx
            item["customer_id"] = customer_id

        return final_recommendations

    def validate_with_real_customer(self, sample_customer_id: str = None, top_n: int = 5):
        """
        Validates the engine using a real customer from the dataset.
        Verifies:
        1. Customer has actual purchase history.
        2. Recommendations are successfully produced.
        3. Recommended products are strictly disjoint from previously purchased products.
        """
        print("\n==========================================")
        print("RUNNING RECOMMENDATION ENGINE VALIDATION")
        print("==========================================")

        # Select a suitable customer with history and rules/similarities if not specified
        if not sample_customer_id or sample_customer_id not in self.customer_history:
            # Prefer a customer with similarity or rule triggers
            candidate_custs = [c for c in self.similarity_graph.keys() if len(self.customer_history.get(c, set())) >= 2]
            if not candidate_custs:
                candidate_custs = [c for c in self.customer_history.keys() if len(self.customer_history.get(c, set())) >= 1]
            sample_customer_id = candidate_custs[0]

        history = self.customer_history.get(sample_customer_id, set())
        recs = self.recommend(sample_customer_id, top_n=top_n)

        rec_prod_ids = {r["product_id"] for r in recs}
        overlap = history & rec_prod_ids

        print(f"Target Customer ID          : {sample_customer_id}")
        print(f"Purchased Products Count    : {len(history)}")
        print(f"Recommendations Generated   : {len(recs)}")
        print(f"History Overlap Verification : {len(overlap)} overlapping products found")
        assert len(overlap) == 0, f"VALIDATION ERROR: Recommended products contain previously purchased items: {overlap}"
        print("Overlap Verification Passed : All recommended products are NEW to the customer! [PASSED]\n")

        # Display Single Customer Formatted Box
        self.display_customer_recommendations(sample_customer_id, recs)

    def display_customer_recommendations(self, customer_id: str, recommendations: list):
        """
        Prints the exact required formatted recommendation output.
        """
        history = list(self.customer_history.get(customer_id, set()))

        print("==========================================")
        print("SHOPLYTICS RECOMMENDATION ENGINE")
        print("==========================================")
        print(f"\nCustomer:\n{customer_id}")
        
        print("\nPreviously purchased products:")
        if history:
            for p in history:
                cat = self.product_categories.get(p, "general")
                print(f"  - {p} (Category: {cat})")
        else:
            print("  (New / Cold-start customer with no previous purchase history)")

        print("\nRecommended products:")
        print(f"{'Rank':<5} | {'Product ID':<34} | {'Score':<7} | {'Category':<22} | {'Reason / Source'}")
        print("-" * 115)

        for r in recommendations:
            print(f"{r['rank']:<5} | {r['product_id']:<34} | {r['recommendation_score']:<7.4f} | {r['product_category']:<22} | {r['recommendation_source']}")

        print("==========================================\n")

    def run_batch_recommendations(self, limit: int = 1000, top_n: int = 10) -> (pd.DataFrame, pd.DataFrame):
        """
        Generates recommendations for a batch of customers and builds result DataFrames.
        """
        print(f"\n[STEP 5] Generating Batch Recommendations (Limit: {limit:,} customers, Top-N: {top_n})...")
        t0 = time.perf_counter()

        all_records = []
        cust_list = list(self.customer_history.keys())
        
        # Sort to prioritize customers with similarity / rule potential, then by purchase volume
        cust_list.sort(key=lambda c: (
            1 if c in self.similarity_graph else 0,
            len(self.customer_history[c])
        ), reverse=True)

        target_custs = cust_list[:limit]
        processed_count = 0

        for c in target_custs:
            recs = self.recommend(c, top_n=top_n)
            all_records.extend(recs)
            processed_count += 1

        exec_time = time.perf_counter() - t0
        print(f"Batch generation completed in {exec_time:.2f} seconds ({len(all_records):,} total recommendation rows).")

        df_recs = pd.DataFrame(all_records)[[
            "customer_id", "rank", "product_id", "product_category",
            "recommendation_score", "apriori_score", "similarity_score",
            "popularity_score", "recommendation_source"
        ]]

        unique_recs = df_recs["product_id"].nunique() if not df_recs.empty else 0
        avg_score = round(df_recs["recommendation_score"].mean(), 4) if not df_recs.empty else 0.0

        df_summary = pd.DataFrame([{
            "customers_processed": processed_count,
            "recommendations_generated": len(df_recs),
            "top_n": top_n,
            "customers_with_recommendations": df_recs["customer_id"].nunique(),
            "unique_products_recommended": unique_recs,
            "average_recommendation_score": avg_score,
            "execution_time_seconds": round(exec_time, 2)
        }])

        return df_recs, df_summary


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Shoplytics Hybrid Product Recommendation Engine")
    parser.add_argument("--customer", type=str, default=None, help="Target Customer ID to generate recommendations for")
    parser.add_argument("--top-n", type=int, default=10, help="Number of recommendations to generate (default: 10)")
    parser.add_argument("--limit", type=int, default=1000, help="Batch customer limit (default: 1000)")
    parser.add_argument("--all", action="store_true", help="Process all active customers in the dataset")
    args = parser.parse_args()

    print("==========================================")
    print("  SHOPLYTICS: HYBRID RECOMMENDATION ENGINE")
    print("==========================================")

    start_datetime = datetime.now()
    start_time = time.perf_counter()
    print(f"Execution Start Time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Initialize Engine and Load Data
    engine = ShoplyticsRecommendationEngine()
    engine.load_data()

    # 2. Run Built-in Real Customer Validation Test
    engine.validate_with_real_customer(sample_customer_id=args.customer, top_n=min(args.top_n, 5))

    # 3. Single Customer Mode (if requested via CLI)
    if args.customer:
        print(f"[CLI REQUEST] Generating Top-{args.top_n} recommendations for customer: {args.customer}")
        recs = engine.recommend(args.customer, top_n=args.top_n)
        engine.display_customer_recommendations(args.customer, recs)

    # 4. Batch Recommendation Generation
    batch_limit = len(engine.customer_history) if args.all else args.limit
    df_recs, df_summary = engine.run_batch_recommendations(limit=batch_limit, top_n=args.top_n)

    end_time = time.perf_counter()
    end_datetime = datetime.now()
    total_execution_time = end_time - start_time

    # 5. Save Results Locally
    output_dir = r"C:\Projects\Shoplytics\results\recommendation_engine"
    os.makedirs(output_dir, exist_ok=True)

    recs_file = os.path.join(output_dir, "recommendations.csv")
    summary_file = os.path.join(output_dir, "recommendation_summary.csv")

    df_recs.to_csv(recs_file, index=False)
    
    # Add timestamps to summary
    df_summary["start_time"] = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    df_summary["end_time"] = end_datetime.strftime("%Y-%m-%d %H:%M:%S")
    df_summary["total_pipeline_time_seconds"] = round(total_execution_time, 2)
    df_summary.to_csv(summary_file, index=False)

    print("\n==========================================")
    print("RECOMMENDATION RESULTS SAVED LOCALLY")
    print("==========================================")
    print(f"1. Recommendations File : {recs_file} ({len(df_recs):,} rows)")
    print(f"2. Summary File         : {summary_file}")
    print("\n==========================================")
    print("RECOMMENDATION SUMMARY METRICS")
    print("==========================================")
    print(f"Customers Processed            : {df_summary['customers_processed'].iloc[0]:,}")
    print(f"Recommendations Generated      : {df_summary['recommendations_generated'].iloc[0]:,}")
    print(f"Unique Products Recommended    : {df_summary['unique_products_recommended'].iloc[0]:,}")
    print(f"Average Recommendation Score   : {df_summary['average_recommendation_score'].iloc[0]:.4f}")
    print(f"Total Pipeline Execution Time  : {total_execution_time:.2f} seconds")
    print("==========================================")


if __name__ == "__main__":
    main()

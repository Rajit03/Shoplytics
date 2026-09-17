"""
==============================================================================
SHOPLYTICS: Distributed Big Data Analytics Platform for E-Commerce
ALGORITHM: Apriori (Market Basket Analysis & Association Rule Mining)
==============================================================================

WHAT IT DOES:
The Apriori algorithm is a data mining algorithm used to discover frequent 
itemsets and generate strong association rules (e.g., "If a customer buys Product A, 
they are also likely to buy Product B").
Key Metrics:
- Support(A -> B)    = P(A ∩ B) = Count(A ∩ B) / Total Transactions
- Confidence(A -> B) = P(B | A) = Support(A ∩ B) / Support(A)
- Lift(A -> B)       = Confidence(A -> B) / Support(B) = P(A ∩ B) / (P(A) * P(B))
  * Lift > 1: Strong positive association (co-purchased much more than random chance).

WHY WE NEED IT IN SHOPLYTICS:
In an e-commerce platform like Olist/Shoplytics, understanding product affinity enables:
1. Cross-selling & "Frequently Bought Together" recommendation widgets.
2. Bundle promotions & dynamic category placement.
3. Inventory co-location in fulfillment warehouses to optimize packing efficiency.

WHERE IT FITS:
Transactions Stream -> Basket Grouping -> Apriori Engine -> Recommendation Service / Dashboard
==============================================================================
"""

import os
import sys
import time
from datetime import datetime
from collections import Counter
from itertools import combinations
import pandas as pd


class AprioriEngine:
    """
    Production-grade Apriori Algorithm for Market Basket Analysis.
    Implements:
    - Level-wise candidate generation (Ck) and pruning (Lk).
    - Apriori downward-closure property: All non-empty subsets of a frequent itemset must also be frequent.
    - Association rule mining with Support, Confidence, and Lift calculations.
    """

    def __init__(self, min_support: float = 0.00003, min_confidence: float = 0.10, category_map: dict = None):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.category_map = category_map or {}

        self.transactions = []
        self.total_transactions = 0
        self.frequent_itemsets = {}  # {frozenset(items): count}
        self.itemsets_by_level = {}  # {level: {frozenset(items): count}}
        self.association_rules = []  # list of dicts
        self.total_candidates_generated = 0

    def fit(self, transactions: list):
        """
        Executes the Apriori algorithm over the transaction dataset.
        """
        self.transactions = transactions
        self.total_transactions = len(transactions)
        min_support_count = self.min_support * self.total_transactions

        # ========================================================
        # LEVEL 1: Frequent 1-itemsets (L1)
        # ========================================================
        c1 = Counter()
        for transaction in self.transactions:
            for item in transaction:
                c1[item] += 1

        self.total_candidates_generated += len(c1)
        l1 = {frozenset([item]): count for item, count in c1.items() if count >= min_support_count}
        self.itemsets_by_level[1] = l1
        self.frequent_itemsets.update(l1)

        current_frequent = l1
        k = 2

        # ========================================================
        # LEVEL k >= 2: Iterative Candidate Generation & Pruning
        # ========================================================
        while current_frequent:
            frequent_items = set().union(*current_frequent.keys())
            prev_frequent_set = set(current_frequent.keys())

            # Count candidate k-itemsets occurring in transactions
            candidate_counts = Counter()
            for transaction in self.transactions:
                # Filter transaction items to only known frequent items from previous level
                filtered_items = sorted([item for item in transaction if item in frequent_items])
                if len(filtered_items) >= k:
                    for combo in combinations(filtered_items, k):
                        candidate_itemset = frozenset(combo)
                        # Downward-closure verification: all (k-1) subsets must be in L_{k-1}
                        if all(frozenset(subset) in prev_frequent_set for subset in combinations(combo, k - 1)):
                            candidate_counts[candidate_itemset] += 1

            self.total_candidates_generated += len(candidate_counts)
            if not candidate_counts:
                break

            # Prune candidates to form Lk
            lk = {itemset: count for itemset, count in candidate_counts.items() if count >= min_support_count}

            if not lk:
                break

            self.itemsets_by_level[k] = lk
            self.frequent_itemsets.update(lk)
            current_frequent = lk
            k += 1

        # ========================================================
        # ASSOCIATION RULE GENERATION
        # ========================================================
        self._generate_association_rules()

    def _generate_association_rules(self):
        """
        Generates association rules A -> B from frequent itemsets with size >= 2.
        Calculates Support, Confidence, and Lift.
        """
        self.association_rules = []

        for itemset, support_count in self.frequent_itemsets.items():
            if len(itemset) < 2:
                continue

            rule_support = support_count / self.total_transactions

            # Generate all non-empty proper antecedent subsets
            for r in range(1, len(itemset)):
                for antecedent_tuple in combinations(itemset, r):
                    antecedent = frozenset(antecedent_tuple)
                    consequent = frozenset(itemset - antecedent)

                    antecedent_count = self.frequent_itemsets.get(antecedent, 0)
                    consequent_count = self.frequent_itemsets.get(consequent, 0)

                    if antecedent_count == 0 or consequent_count == 0:
                        continue

                    antecedent_support = antecedent_count / self.total_transactions
                    consequent_support = consequent_count / self.total_transactions

                    confidence = rule_support / antecedent_support
                    lift = confidence / consequent_support

                    if confidence >= self.min_confidence:
                        ant_list = sorted(list(antecedent))
                        con_list = sorted(list(consequent))

                        ant_cats = [self.category_map.get(pid, "unknown") for pid in ant_list]
                        con_cats = [self.category_map.get(pid, "unknown") for pid in con_list]

                        self.association_rules.append({
                            "antecedent": ";".join(ant_list),
                            "antecedent_categories": ";".join(ant_cats),
                            "consequent": ";".join(con_list),
                            "consequent_categories": ";".join(con_cats),
                            "antecedent_support": round(antecedent_support, 6),
                            "consequent_support": round(consequent_support, 6),
                            "support": round(rule_support, 6),
                            "support_count": support_count,
                            "confidence": round(confidence, 4),
                            "lift": round(lift, 2)
                        })

        # Sort rules by Lift descending, then Confidence descending
        self.association_rules.sort(key=lambda r: (r["lift"], r["confidence"]), reverse=True)


# ==============================================================================
# MAIN EXECUTION & BENCHMARKING PIPELINE
# ==============================================================================

def main():
    print("==========================================")
    print("       SHOPLYTICS: APRIORI ALGORITHM      ")
    print("==========================================")

    start_datetime = datetime.now()
    start_time = time.perf_counter()
    print(f"Execution Start Time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Load Datasets
    order_items_file = r"C:\Projects\Shoplytics\data\processed\order_items_clean.csv"
    products_file = r"C:\Projects\Shoplytics\data\processed\products_clean.csv"

    print("\n[STEP 1] Loading Olist Order-Items and Product Data...")
    print(f"Order Items File : {order_items_file}")
    print(f"Products File    : {products_file}")

    if not os.path.exists(order_items_file):
        print(f"ERROR: {order_items_file} not found.")
        sys.exit(1)

    df_items = pd.read_csv(order_items_file)
    print(f"Total order-items rows: {len(df_items):,}")

    # Build Product ID -> Category Map
    category_map = {}
    if os.path.exists(products_file):
        df_prod = pd.read_csv(products_file)
        if "product_category_name_english" in df_prod.columns:
            category_map = dict(zip(df_prod["product_id"].astype(str), df_prod["product_category_name_english"].fillna("unknown")))
        elif "product_category_name" in df_prod.columns:
            category_map = dict(zip(df_prod["product_id"].astype(str), df_prod["product_category_name"].fillna("unknown")))
    print(f"Product metadata categories loaded: {len(category_map):,} products")

    # 2. Construct Transactions (Baskets)
    print("\n[STEP 2] Constructing Unique Product Baskets per Order...")
    df_clean = df_items.dropna(subset=["order_id", "product_id"]).copy()
    df_clean["product_id"] = df_clean["product_id"].astype(str).str.strip()
    df_clean = df_clean[df_clean["product_id"] != ""]

    transactions = df_clean.groupby("order_id")["product_id"].apply(lambda x: list(set(x))).tolist()
    transactions = [t for t in transactions if len(t) > 0]
    total_transactions = len(transactions)

    multi_item_baskets = sum(1 for t in transactions if len(t) >= 2)
    print(f"Total transactions (orders)      : {total_transactions:,}")
    print(f"Multi-item baskets (>= 2 items)  : {multi_item_baskets:,}")

    # 3. Configure Apriori Parameters
    min_support = 0.00003
    min_confidence = 0.10

    print("\n[STEP 3] Initializing Apriori Engine...")
    print(f"Minimum Support Threshold        : {min_support} (>= {int(min_support * total_transactions)} transactions)")
    print(f"Minimum Confidence Threshold     : {min_confidence * 100:.1f} %")

    # 4. Run Apriori
    engine = AprioriEngine(min_support=min_support, min_confidence=min_confidence, category_map=category_map)
    engine.fit(transactions)

    end_time = time.perf_counter()
    end_datetime = datetime.now()
    execution_time_sec = end_time - start_time

    # 5. Extract Statistics
    l1_count = len(engine.itemsets_by_level.get(1, {}))
    l2_count = len(engine.itemsets_by_level.get(2, {}))
    l3_count = len(engine.itemsets_by_level.get(3, {}))
    total_frequent_itemsets = len(engine.frequent_itemsets)
    total_association_rules = len(engine.association_rules)

    print("\n==========================================")
    print("APRIORI RESULTS")
    print("==========================================")
    print(f"Total transactions       : {total_transactions:,}")
    print(f"Minimum support          : {min_support}")
    print(f"Minimum confidence       : {min_confidence}")
    print(f"\nFrequent 1-itemsets      : {l1_count:,}")
    print(f"Frequent 2-itemsets      : {l2_count:,}")
    print(f"Frequent 3-itemsets      : {l3_count:,}")
    print(f"\nTotal candidate itemsets : {engine.total_candidates_generated:,}")
    print(f"Total frequent itemsets  : {total_frequent_itemsets:,}")
    print(f"Total association rules  : {total_association_rules:,}")
    print(f"Execution time (seconds) : {execution_time_sec:.2f} s")

    # 6. Display Top Association Rules
    print("\n==========================================")
    print("TOP ASSOCIATION RULES (HIGHEST LIFT)")
    print("==========================================")

    for idx, rule in enumerate(engine.association_rules[:10], 1):
        ant_id = rule["antecedent"]
        con_id = rule["consequent"]
        ant_cat = rule["antecedent_categories"]
        con_cat = rule["consequent_categories"]

        print(f"\nRule #{idx}:")
        print(f"  {ant_id} ({ant_cat})  ==>  {con_id} ({con_cat})")
        print(f"  Support    : {rule['support']:.6f} ({rule['support_count']} orders)")
        print(f"  Confidence : {rule['confidence'] * 100:.2f} %")
        print(f"  Lift       : {rule['lift']:.2f}x")

    # 7. Save Result Files Locally
    output_dir = r"C:\Projects\Shoplytics\results\apriori"
    os.makedirs(output_dir, exist_ok=True)

    # 7.1 frequent_itemsets.csv
    itemset_rows = []
    for k, itemsets in engine.itemsets_by_level.items():
        for itemset, count in itemsets.items():
            items = sorted(list(itemset))
            cats = [category_map.get(pid, "unknown") for pid in items]
            itemset_rows.append({
                "itemset": ";".join(items),
                "itemset_categories": ";".join(cats),
                "itemset_size": k,
                "support": round(count / total_transactions, 6),
                "support_count": count
            })

    df_itemsets = pd.DataFrame(itemset_rows)
    df_itemsets.sort_values(by=["itemset_size", "support_count"], ascending=[True, False], inplace=True)
    itemsets_file = os.path.join(output_dir, "frequent_itemsets.csv")
    df_itemsets.to_csv(itemsets_file, index=False)

    # 7.2 association_rules.csv
    df_rules = pd.DataFrame(engine.association_rules)
    rules_file = os.path.join(output_dir, "association_rules.csv")
    df_rules.to_csv(rules_file, index=False)

    # 7.3 apriori_summary.csv
    summary_data = [{
        "total_transactions": total_transactions,
        "multi_item_baskets": multi_item_baskets,
        "minimum_support": min_support,
        "minimum_confidence": min_confidence,
        "frequent_1_itemsets": l1_count,
        "frequent_2_itemsets": l2_count,
        "frequent_3_itemsets": l3_count,
        "total_frequent_itemsets": total_frequent_itemsets,
        "total_association_rules": total_association_rules,
        "total_candidates_generated": engine.total_candidates_generated,
        "start_time": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "execution_time_seconds": round(execution_time_sec, 2)
    }]

    df_summary = pd.DataFrame(summary_data)
    summary_file = os.path.join(output_dir, "apriori_summary.csv")
    df_summary.to_csv(summary_file, index=False)

    print("\n==========================================")
    print("APRIORI RESULT FILES SAVED LOCALLY")
    print("==========================================")
    print(f"1. Frequent Itemsets : {itemsets_file}")
    print(f"2. Association Rules : {rules_file}")
    print(f"3. Apriori Summary   : {summary_file}")
    print("\n==========================================")
    print("APRIORI EXECUTION COMPLETED SUCCESSFULLY")
    print("==========================================")


if __name__ == "__main__":
    main()

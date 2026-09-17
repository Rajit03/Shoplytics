"""
Shoplytics: PostgreSQL Automated Query Tests & Performance Benchmarking
Executes core analytical and operational queries, measures latency, and records EXPLAIN ANALYZE metrics.
"""

import os
import sys
import time
import csv
import psycopg2
from psycopg2.extras import RealDictCursor


def load_env_file(filepath=".env"):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_env_file(os.path.join(BASE_DIR, ".env"))

PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = int(os.getenv("PGPORT", "5432"))
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD", "postgres")
PGDATABASE = os.getenv("PGDATABASE", "shoplytics")

RESULTS_DIR = os.path.join(BASE_DIR, "results", "postgresql")
os.makedirs(RESULTS_DIR, exist_ok=True)


def get_db_connection():
    return psycopg2.connect(
        host=PGHOST,
        port=PGPORT,
        user=PGUSER,
        password=PGPASSWORD,
        dbname=PGDATABASE
    )


def run_benchmark_query(cur, query_name, sql_query, params=None):
    """Run EXPLAIN ANALYZE and timed execution for performance measurement."""
    # Check execution plan
    explain_sql = f"EXPLAIN ANALYZE {sql_query}"
    index_used = "No / Seq Scan"
    try:
        cur.execute(explain_sql, params)
        plan_rows = cur.fetchall()
        plan_text = " ".join(row[0] for row in plan_rows)
        if "Index Scan" in plan_text or "Index Only Scan" in plan_text or "Bitmap Index Scan" in plan_text:
            index_used = "Yes / Index Scan"
    except Exception as e:
        plan_text = str(e)

    # Measure raw execution time over multiple passes
    t_start = time.perf_counter()
    cur.execute(sql_query, params)
    rows = cur.fetchall()
    exec_time_ms = round((time.perf_counter() - t_start) * 1000, 3)

    return {
        "query_name": query_name,
        "execution_time_ms": exec_time_ms,
        "index_used": index_used,
        "status": "SUCCESS",
        "row_count": len(rows),
        "sample": rows[:3]
    }


def main():
    print("==========================================")
    print("SHOPLYTICS: POSTGRESQL QUERY TESTS")
    print("==========================================")
    print(f"Connecting to database '{PGDATABASE}' on {PGHOST}:{PGPORT}...\n")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        sys.exit(1)

    benchmarks = []

    # 1. Count rows in every table
    print("------------------------------------------")
    print("1. Table Row Counts")
    print("------------------------------------------")
    count_sql = """
        SELECT 'customers' AS tbl, COUNT(*) AS cnt FROM customers
        UNION ALL SELECT 'products', COUNT(*) FROM products
        UNION ALL SELECT 'orders', COUNT(*) FROM orders
        UNION ALL SELECT 'analytics', COUNT(*) FROM analytics
        UNION ALL SELECT 'customer_segments', COUNT(*) FROM customer_segments
        UNION ALL SELECT 'cluster_profiles', COUNT(*) FROM cluster_profiles
        UNION ALL SELECT 'recommendations', COUNT(*) FROM recommendations
        UNION ALL SELECT 'association_rules', COUNT(*) FROM association_rules;
    """
    cur.execute(count_sql)
    for tbl, cnt in cur.fetchall():
        print(f"  {tbl:<20}: {cnt:,}")

    # 2. Customer lookup by customer_unique_id
    print("\n------------------------------------------")
    print("2. Customer Lookup by Unique ID")
    print("------------------------------------------")
    q2_sql = "SELECT * FROM customers WHERE customer_unique_id = %s"
    target_cid = "0000366f3b9a7992bf8c76cfdf3221e2"
    res2 = run_benchmark_query(cur, "Customer Lookup by ID", q2_sql, (target_cid,))
    benchmarks.append(res2)
    print(f"  Result: {res2['sample']}")
    print(f"  Execution Time: {res2['execution_time_ms']} ms | Index Used: {res2['index_used']}")

    # 3. Top-spending customers
    print("\n------------------------------------------")
    print("3. Top-Spending Customers")
    print("------------------------------------------")
    q3_sql = "SELECT customer_unique_id, total_spending, total_orders, cluster FROM customers ORDER BY total_spending DESC LIMIT 5"
    res3 = run_benchmark_query(cur, "Top Spending Customers", q3_sql)
    benchmarks.append(res3)
    for row in res3['sample']:
        print(f"  Customer: {row[0]}, Spending: ${row[1]:,.2f}, Orders: {row[2]}, Cluster: {row[3]}")
    print(f"  Execution Time: {res3['execution_time_ms']} ms")

    # 4. Customers in a specific cluster
    print("\n------------------------------------------")
    print("4. Customers in Cluster 2 (High Value)")
    print("------------------------------------------")
    q4_sql = "SELECT customer_unique_id, total_spending, average_order_value FROM customer_segments WHERE cluster = 2 ORDER BY total_spending DESC LIMIT 5"
    res4 = run_benchmark_query(cur, "Customer Cluster Lookup", q4_sql)
    benchmarks.append(res4)
    for row in res4['sample']:
        print(f"  Customer: {row[0]}, Spending: ${row[1]:,.2f}, AOV: ${row[2]:,.2f}")
    print(f"  Execution Time: {res4['execution_time_ms']} ms | Index Used: {res4['index_used']}")

    # 5. Products by Category
    print("\n------------------------------------------")
    print("5. Products by Category ('health_beauty')")
    print("------------------------------------------")
    q5_sql = "SELECT product_id, product_category_name_english, product_weight_g FROM products WHERE product_category_name_english = 'health_beauty' LIMIT 5"
    res5 = run_benchmark_query(cur, "Products by Category", q5_sql)
    benchmarks.append(res5)
    for row in res5['sample']:
        print(f"  Product ID: {row[0]}, Category: {row[1]}, Weight: {row[2]}g")
    print(f"  Execution Time: {res5['execution_time_ms']} ms | Index Used: {res5['index_used']}")

    # 6. Recommendations for customer
    print("\n------------------------------------------")
    print("6. Recommendations for Customer")
    print("------------------------------------------")
    q6_sql = "SELECT customer_id, rank, product_id, product_category, recommendation_score, recommendation_source FROM recommendations WHERE customer_id = '0f8758e5b1c6c6b2156a9dddce128558' ORDER BY rank"
    res6 = run_benchmark_query(cur, "Recommendation Lookup by Customer ID", q6_sql)
    benchmarks.append(res6)
    for row in res6['sample']:
        print(f"  Rank {row[1]}: Product {row[2]} ({row[3]}) | Score: {row[4]} | Source: {row[5]}")
    print(f"  Execution Time: {res6['execution_time_ms']} ms | Index Used: {res6['index_used']}")

    # 7. Top Association Rules (Apriori)
    print("\n------------------------------------------")
    print("7. Top Association Rules (Apriori)")
    print("------------------------------------------")
    q7_sql = "SELECT antecedent, consequent, support, confidence, lift FROM association_rules ORDER BY lift DESC LIMIT 5"
    res7 = run_benchmark_query(cur, "Top Association Rules", q7_sql)
    benchmarks.append(res7)
    for row in res7['sample']:
        print(f"  {row[0]} -> {row[1]} | Support: {row[2]}, Conf: {row[3]}, Lift: {row[4]}")
    print(f"  Execution Time: {res7['execution_time_ms']} ms")

    # 8. Retrieve Total Sales Analytics
    print("\n------------------------------------------")
    print("8. Total Sales & Revenue Analytics")
    print("------------------------------------------")
    q8_sql = "SELECT COUNT(DISTINCT order_id), COUNT(*), ROUND(SUM(total_item_value), 2), ROUND(SUM(price), 2) FROM analytics"
    res8 = run_benchmark_query(cur, "Total Sales Aggregation", q8_sql)
    benchmarks.append(res8)
    print(f"  Orders: {res8['sample'][0][0]:,}, Items: {res8['sample'][0][1]:,}, Gross: ${res8['sample'][0][2]:,}, Net: ${res8['sample'][0][3]:,}")
    print(f"  Execution Time: {res8['execution_time_ms']} ms")

    # 9. Monthly Sales Breakdown
    print("\n------------------------------------------")
    print("9. Monthly Sales Breakdown")
    print("------------------------------------------")
    q9_sql = "SELECT order_year, order_month, order_month_name, COUNT(DISTINCT order_id), ROUND(SUM(total_item_value), 2) FROM analytics WHERE order_year IS NOT NULL GROUP BY order_year, order_month, order_month_name ORDER BY order_year, order_month LIMIT 5"
    res9 = run_benchmark_query(cur, "Monthly Sales Query", q9_sql)
    benchmarks.append(res9)
    for row in res9['sample']:
        print(f"  {row[0]}-{row[1]:02d} ({row[2]}): Orders={row[3]:,}, Revenue=${row[4]:,.2f}")
    print(f"  Execution Time: {res9['execution_time_ms']} ms")

    # 10. Top Selling Products
    print("\n------------------------------------------")
    print("10. Top Selling Products")
    print("------------------------------------------")
    q10_sql = "SELECT product_id, product_category_name_english, COUNT(*) as units_sold, ROUND(SUM(total_item_value), 2) as revenue FROM analytics GROUP BY product_id, product_category_name_english ORDER BY revenue DESC LIMIT 5"
    res10 = run_benchmark_query(cur, "Top Products Query", q10_sql)
    benchmarks.append(res10)
    for row in res10['sample']:
        print(f"  Product: {row[0]} ({row[1]}) | Units: {row[2]}, Revenue: ${row[3]:,.2f}")
    print(f"  Execution Time: {res10['execution_time_ms']} ms")

    # 11. Order Status Statistics
    print("\n------------------------------------------")
    print("11. Order Status Distribution")
    print("------------------------------------------")
    q11_sql = "SELECT order_status, COUNT(*) FROM orders GROUP BY order_status ORDER BY COUNT(*) DESC"
    res11 = run_benchmark_query(cur, "Order Status Distribution", q11_sql)
    benchmarks.append(res11)
    for row in res11['sample']:
        print(f"  Status '{row[0]}': {row[1]:,} orders")
    print(f"  Execution Time: {res11['execution_time_ms']} ms")

    # 12. JOIN: Customers & Customer Segments
    print("\n------------------------------------------")
    print("12. JOIN: Customers with Customer Segments & Profiles")
    print("------------------------------------------")
    q12_sql = """
        SELECT c.customer_unique_id, c.total_spending, cs.cluster, cp.customers as cluster_size, cp.avg_spending
        FROM customers c
        JOIN customer_segments cs ON c.customer_unique_id = cs.customer_unique_id
        JOIN cluster_profiles cp ON cs.cluster = cp.cluster
        ORDER BY c.total_spending DESC
        LIMIT 5;
    """
    res12 = run_benchmark_query(cur, "JOIN Customers with Segments", q12_sql)
    benchmarks.append(res12)
    for row in res12['sample']:
        print(f"  Customer: {row[0]} | Spending: ${row[1]:,.2f} | Cluster {row[2]} (Total Cluster Pop: {row[3]:,}, Cluster Avg Spend: ${row[4]:,.2f})")
    print(f"  Execution Time: {res12['execution_time_ms']} ms")

    # 13. JOIN: Recommendations & Products
    print("\n------------------------------------------")
    print("13. JOIN: Recommendations with Products")
    print("------------------------------------------")
    q13_sql = """
        SELECT r.customer_id, r.rank, r.product_id, p.product_category_name_english, p.product_weight_g, r.recommendation_score
        FROM recommendations r
        JOIN products p ON r.product_id = p.product_id
        WHERE r.customer_id = '0f8758e5b1c6c6b2156a9dddce128558'
        ORDER BY r.rank;
    """
    res13 = run_benchmark_query(cur, "JOIN Recommendations with Products", q13_sql)
    benchmarks.append(res13)
    for row in res13['sample']:
        print(f"  Rank {row[1]}: {row[2]} ({row[3]}, weight: {row[4]}g) - Score: {row[5]}")
    print(f"  Execution Time: {res13['execution_time_ms']} ms")

    cur.close()
    conn.close()

    # Save postgresql_query_performance.csv
    perf_path = os.path.join(RESULTS_DIR, "postgresql_query_performance.csv")
    with open(perf_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query_name", "execution_time_ms", "index_used", "status"])
        writer.writeheader()
        for b in benchmarks:
            writer.writerow({
                "query_name": b["query_name"],
                "execution_time_ms": b["execution_time_ms"],
                "index_used": b["index_used"],
                "status": b["status"]
            })
    print(f"\n==========================================")
    print(f"Query performance saved to: {perf_path}")
    print("==========================================")


if __name__ == "__main__":
    main()

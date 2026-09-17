"""
Shoplytics: PostgreSQL Database Loader
Loads preprocessed datasets and Big Data algorithm results into PostgreSQL.
"""

import os
import sys
import glob
import time
import csv
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


# =====================================================================
# CONFIGURATION & ENVIRONMENT
# =====================================================================

def load_env_file(filepath=".env"):
    """Load environment variables from a .env file if present."""
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


# =====================================================================
# HELPER PARSERS
# =====================================================================

def parse_str(val):
    if val is None:
        return None
    s = str(val).strip()
    return s if s != "" else None

def parse_int(val):
    if val is None:
        return None
    s = str(val).strip()
    if s == "" or s.lower() == "none" or s.lower() == "nan":
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None

def parse_float(val):
    if val is None:
        return None
    s = str(val).strip()
    if s == "" or s.lower() == "none" or s.lower() == "nan":
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None

def parse_timestamp(val):
    if val is None:
        return None
    s = str(val).strip()
    if s == "" or s.lower() == "none" or s.lower() == "nan":
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def parse_date(val):
    ts = parse_timestamp(val)
    return ts.date() if ts else None


# =====================================================================
# DATABASE CREATION & CONNECTION
# =====================================================================

def get_admin_connection():
    """Connect to default 'postgres' database to check/create shoplytics."""
    return psycopg2.connect(
        host=PGHOST,
        port=PGPORT,
        user=PGUSER,
        password=PGPASSWORD,
        dbname="postgres"
    )

def get_db_connection():
    """Connect to 'shoplytics' database."""
    return psycopg2.connect(
        host=PGHOST,
        port=PGPORT,
        user=PGUSER,
        password=PGPASSWORD,
        dbname=PGDATABASE
    )

def ensure_database_exists():
    """Create database 'shoplytics' if not present."""
    print(f"Connecting to PostgreSQL server at {PGHOST}:{PGPORT} as user '{PGUSER}'...")
    try:
        conn = get_admin_connection()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PGDATABASE,))
        exists = cur.fetchone()
        if not exists:
            print(f"Creating database '{PGDATABASE}'...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(PGDATABASE)))
            print(f"Database '{PGDATABASE}' created successfully.")
        else:
            print(f"Database '{PGDATABASE}' already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error ensuring database exists: {e}")
        raise


# =====================================================================
# DDL: TABLE CREATION & INDEXES
# =====================================================================

TABLE_DDL = {
    "customers": """
        CREATE TABLE IF NOT EXISTS customers (
            customer_unique_id VARCHAR(64) PRIMARY KEY,
            total_orders INTEGER,
            total_spending NUMERIC(12, 2),
            total_freight NUMERIC(12, 2),
            total_products INTEGER,
            average_order_value NUMERIC(12, 2),
            cluster INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_customers_cluster ON customers (cluster);
    """,

    "products": """
        CREATE TABLE IF NOT EXISTS products (
            product_id VARCHAR(64) PRIMARY KEY,
            product_category_name VARCHAR(100),
            product_name_lenght INTEGER,
            product_description_lenght INTEGER,
            product_photos_qty INTEGER,
            product_weight_g NUMERIC(10, 2),
            product_length_cm NUMERIC(10, 2),
            product_height_cm NUMERIC(10, 2),
            product_width_cm NUMERIC(10, 2),
            product_category_name_english VARCHAR(100)
        );
        CREATE INDEX IF NOT EXISTS idx_products_category ON products (product_category_name_english);
    """,

    "orders": """
        CREATE TABLE IF NOT EXISTS orders (
            order_id VARCHAR(64) PRIMARY KEY,
            customer_id VARCHAR(64),
            order_status VARCHAR(50),
            order_purchase_timestamp TIMESTAMP,
            order_approved_at TIMESTAMP,
            order_delivered_carrier_date TIMESTAMP,
            order_delivered_customer_date TIMESTAMP,
            order_estimated_delivery_date TIMESTAMP,
            order_year INTEGER,
            order_month INTEGER,
            order_month_name VARCHAR(20),
            order_date DATE,
            order_day INTEGER,
            order_day_of_week VARCHAR(20),
            delivery_days NUMERIC(10, 4),
            estimated_delivery_days NUMERIC(10, 4)
        );
        CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders (customer_id);
        CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (order_status);
        CREATE INDEX IF NOT EXISTS idx_orders_purchase_timestamp ON orders (order_purchase_timestamp);
    """,

    "customer_segments": """
        CREATE TABLE IF NOT EXISTS customer_segments (
            customer_unique_id VARCHAR(64) PRIMARY KEY,
            total_orders INTEGER,
            total_spending NUMERIC(12, 2),
            total_freight NUMERIC(12, 2),
            total_products INTEGER,
            average_order_value NUMERIC(12, 2),
            cluster INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_cust_segments_cluster ON customer_segments (cluster);
    """,

    "cluster_profiles": """
        CREATE TABLE IF NOT EXISTS cluster_profiles (
            cluster INTEGER PRIMARY KEY,
            customers BIGINT,
            avg_orders NUMERIC(10, 4),
            avg_spending NUMERIC(12, 4),
            avg_freight NUMERIC(12, 4),
            avg_products NUMERIC(10, 4),
            avg_order_value NUMERIC(12, 4),
            min_spending NUMERIC(12, 2),
            max_spending NUMERIC(12, 2)
        );
    """,

    "recommendations": """
        CREATE TABLE IF NOT EXISTS recommendations (
            id BIGSERIAL PRIMARY KEY,
            customer_id VARCHAR(64),
            rank INTEGER,
            product_id VARCHAR(64),
            product_category VARCHAR(100),
            recommendation_score NUMERIC(8, 4),
            apriori_score NUMERIC(8, 4),
            similarity_score NUMERIC(8, 4),
            popularity_score NUMERIC(8, 4),
            recommendation_source VARCHAR(100)
        );
        CREATE INDEX IF NOT EXISTS idx_recs_customer_id ON recommendations (customer_id);
        CREATE INDEX IF NOT EXISTS idx_recs_rank ON recommendations (rank);
        CREATE INDEX IF NOT EXISTS idx_recs_product_id ON recommendations (product_id);
    """,

    "association_rules": """
        CREATE TABLE IF NOT EXISTS association_rules (
            id BIGSERIAL PRIMARY KEY,
            antecedent TEXT,
            antecedent_categories TEXT,
            consequent TEXT,
            consequent_categories TEXT,
            antecedent_support NUMERIC(12, 6),
            consequent_support NUMERIC(12, 6),
            support NUMERIC(12, 6),
            support_count INTEGER,
            confidence NUMERIC(10, 6),
            lift NUMERIC(12, 4)
        );
        CREATE INDEX IF NOT EXISTS idx_rules_support ON association_rules (support);
        CREATE INDEX IF NOT EXISTS idx_rules_confidence ON association_rules (confidence);
        CREATE INDEX IF NOT EXISTS idx_rules_lift ON association_rules (lift);
    """,

    "analytics": """
        CREATE TABLE IF NOT EXISTS analytics (
            id BIGSERIAL PRIMARY KEY,
            order_id VARCHAR(64),
            order_item_id INTEGER,
            product_id VARCHAR(64),
            seller_id VARCHAR(64),
            shipping_limit_date TIMESTAMP,
            price NUMERIC(10, 2),
            freight_value NUMERIC(10, 2),
            total_item_value NUMERIC(10, 2),
            customer_id VARCHAR(64),
            order_status VARCHAR(50),
            order_purchase_timestamp TIMESTAMP,
            order_approved_at TIMESTAMP,
            order_delivered_carrier_date TIMESTAMP,
            order_delivered_customer_date TIMESTAMP,
            order_estimated_delivery_date TIMESTAMP,
            order_year INTEGER,
            order_month INTEGER,
            order_month_name VARCHAR(20),
            order_date DATE,
            order_day INTEGER,
            order_day_of_week VARCHAR(20),
            delivery_days NUMERIC(10, 4),
            estimated_delivery_days NUMERIC(10, 4),
            product_category_name_english VARCHAR(100),
            customer_unique_id VARCHAR(64),
            customer_city VARCHAR(100),
            customer_state VARCHAR(10)
        );
        CREATE INDEX IF NOT EXISTS idx_analytics_order_id ON analytics (order_id);
        CREATE INDEX IF NOT EXISTS idx_analytics_product_id ON analytics (product_id);
        CREATE INDEX IF NOT EXISTS idx_analytics_cust_uid ON analytics (customer_unique_id);
        CREATE INDEX IF NOT EXISTS idx_analytics_category ON analytics (product_category_name_english);
        CREATE INDEX IF NOT EXISTS idx_analytics_year_month ON analytics (order_year, order_month);
    """
}

def create_tables(conn):
    """Execute DDL statements to create all tables and indexes."""
    print("\nCreating tables and indexes in 'shoplytics'...")
    cur = conn.cursor()
    for table_name, ddl in TABLE_DDL.items():
        cur.execute(ddl)
    conn.commit()
    cur.close()
    print("All tables and indexes created successfully.")


# =====================================================================
# DATA LOADERS FOR EACH TABLE
# =====================================================================

def load_customer_segments(conn):
    """Load customer segments from Spark results."""
    pattern = os.path.join(BASE_DIR, "results", "spark", "customer_segments", "part-*.csv")
    files = glob.glob(pattern)
    if not files:
        print("Warning: No customer_segments part files found.")
        return 0, 0, 0, 0.0

    start_time = time.time()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE customer_segments;")
    
    rows = []
    read_count = 0
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                read_count += 1
                rows.append((
                    parse_str(r.get("customer_unique_id")),
                    parse_int(r.get("total_orders")),
                    parse_float(r.get("total_spending")),
                    parse_float(r.get("total_freight")),
                    parse_int(r.get("total_products")),
                    parse_float(r.get("average_order_value")),
                    parse_int(r.get("cluster"))
                ))

    query = """
        INSERT INTO customer_segments (
            customer_unique_id, total_orders, total_spending, total_freight,
            total_products, average_order_value, cluster
        ) VALUES %s
        ON CONFLICT (customer_unique_id) DO UPDATE SET
            total_orders = EXCLUDED.total_orders,
            total_spending = EXCLUDED.total_spending,
            total_freight = EXCLUDED.total_freight,
            total_products = EXCLUDED.total_products,
            average_order_value = EXCLUDED.average_order_value,
            cluster = EXCLUDED.cluster;
    """
    execute_values(cur, query, rows, page_size=5000)
    conn.commit()
    cur.close()
    load_time = round(time.time() - start_time, 2)
    return read_count, len(rows), 0, load_time


def load_cluster_profiles(conn):
    """Load cluster profiles from Spark results."""
    pattern = os.path.join(BASE_DIR, "results", "spark", "cluster_profiles", "part-*.csv")
    files = glob.glob(pattern)
    if not files:
        print("Warning: No cluster_profiles part files found.")
        return 0, 0, 0, 0.0

    start_time = time.time()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE cluster_profiles;")
    
    rows = []
    read_count = 0
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                read_count += 1
                rows.append((
                    parse_int(r.get("cluster")),
                    parse_int(r.get("customers")),
                    parse_float(r.get("avg_orders")),
                    parse_float(r.get("avg_spending")),
                    parse_float(r.get("avg_freight")),
                    parse_float(r.get("avg_products")),
                    parse_float(r.get("avg_order_value")),
                    parse_float(r.get("min_spending")),
                    parse_float(r.get("max_spending"))
                ))

    query = """
        INSERT INTO cluster_profiles (
            cluster, customers, avg_orders, avg_spending, avg_freight,
            avg_products, avg_order_value, min_spending, max_spending
        ) VALUES %s
        ON CONFLICT (cluster) DO UPDATE SET
            customers = EXCLUDED.customers,
            avg_orders = EXCLUDED.avg_orders,
            avg_spending = EXCLUDED.avg_spending,
            avg_freight = EXCLUDED.avg_freight,
            avg_products = EXCLUDED.avg_products,
            avg_order_value = EXCLUDED.avg_order_value,
            min_spending = EXCLUDED.min_spending,
            max_spending = EXCLUDED.max_spending;
    """
    execute_values(cur, query, rows, page_size=100)
    conn.commit()
    cur.close()
    load_time = round(time.time() - start_time, 2)
    return read_count, len(rows), 0, load_time


def load_customers(conn):
    """Load customers table from customer_features.csv with cluster mapping."""
    filepath = os.path.join(BASE_DIR, "data", "processed", "customer_features.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing file: {filepath}")

    # Build cluster map from customer_segments table if loaded
    cur = conn.cursor()
    cur.execute("SELECT customer_unique_id, cluster FROM customer_segments;")
    cluster_map = dict(cur.fetchall())
    cur.close()

    start_time = time.time()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE customers;")

    rows = []
    read_count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            read_count += 1
            cid = parse_str(r.get("customer_unique_id"))
            cluster = cluster_map.get(cid, None)
            rows.append((
                cid,
                parse_int(r.get("total_orders")),
                parse_float(r.get("total_spending")),
                parse_float(r.get("total_freight")),
                parse_int(r.get("total_products")),
                parse_float(r.get("average_order_value")),
                cluster
            ))

    query = """
        INSERT INTO customers (
            customer_unique_id, total_orders, total_spending, total_freight,
            total_products, average_order_value, cluster
        ) VALUES %s
        ON CONFLICT (customer_unique_id) DO UPDATE SET
            total_orders = EXCLUDED.total_orders,
            total_spending = EXCLUDED.total_spending,
            total_freight = EXCLUDED.total_freight,
            total_products = EXCLUDED.total_products,
            average_order_value = EXCLUDED.average_order_value,
            cluster = EXCLUDED.cluster;
    """
    execute_values(cur, query, rows, page_size=5000)
    conn.commit()
    cur.close()
    load_time = round(time.time() - start_time, 2)
    return read_count, len(rows), 0, load_time


def load_products(conn):
    """Load products table from products_clean.csv."""
    filepath = os.path.join(BASE_DIR, "data", "processed", "products_clean.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing file: {filepath}")

    start_time = time.time()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE products;")

    rows = []
    read_count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            read_count += 1
            rows.append((
                parse_str(r.get("product_id")),
                parse_str(r.get("product_category_name")),
                parse_int(r.get("product_name_lenght")),
                parse_int(r.get("product_description_lenght")),
                parse_int(r.get("product_photos_qty")),
                parse_float(r.get("product_weight_g")),
                parse_float(r.get("product_length_cm")),
                parse_float(r.get("product_height_cm")),
                parse_float(r.get("product_width_cm")),
                parse_str(r.get("product_category_name_english"))
            ))

    query = """
        INSERT INTO products (
            product_id, product_category_name, product_name_lenght,
            product_description_lenght, product_photos_qty, product_weight_g,
            product_length_cm, product_height_cm, product_width_cm,
            product_category_name_english
        ) VALUES %s
        ON CONFLICT (product_id) DO UPDATE SET
            product_category_name = EXCLUDED.product_category_name,
            product_name_lenght = EXCLUDED.product_name_lenght,
            product_description_lenght = EXCLUDED.product_description_lenght,
            product_photos_qty = EXCLUDED.product_photos_qty,
            product_weight_g = EXCLUDED.product_weight_g,
            product_length_cm = EXCLUDED.product_length_cm,
            product_height_cm = EXCLUDED.product_height_cm,
            product_width_cm = EXCLUDED.product_width_cm,
            product_category_name_english = EXCLUDED.product_category_name_english;
    """
    execute_values(cur, query, rows, page_size=5000)
    conn.commit()
    cur.close()
    load_time = round(time.time() - start_time, 2)
    return read_count, len(rows), 0, load_time


def load_orders(conn):
    """Load orders table from orders_clean.csv."""
    filepath = os.path.join(BASE_DIR, "data", "processed", "orders_clean.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing file: {filepath}")

    start_time = time.time()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE orders;")

    rows = []
    read_count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            read_count += 1
            rows.append((
                parse_str(r.get("order_id")),
                parse_str(r.get("customer_id")),
                parse_str(r.get("order_status")),
                parse_timestamp(r.get("order_purchase_timestamp")),
                parse_timestamp(r.get("order_approved_at")),
                parse_timestamp(r.get("order_delivered_carrier_date")),
                parse_timestamp(r.get("order_delivered_customer_date")),
                parse_timestamp(r.get("order_estimated_delivery_date")),
                parse_int(r.get("order_year")),
                parse_int(r.get("order_month")),
                parse_str(r.get("order_month_name")),
                parse_date(r.get("order_date")),
                parse_int(r.get("order_day")),
                parse_str(r.get("order_day_of_week")),
                parse_float(r.get("delivery_days")),
                parse_float(r.get("estimated_delivery_days"))
            ))

    query = """
        INSERT INTO orders (
            order_id, customer_id, order_status,
            order_purchase_timestamp, order_approved_at,
            order_delivered_carrier_date, order_delivered_customer_date,
            order_estimated_delivery_date, order_year, order_month,
            order_month_name, order_date, order_day, order_day_of_week,
            delivery_days, estimated_delivery_days
        ) VALUES %s
        ON CONFLICT (order_id) DO UPDATE SET
            customer_id = EXCLUDED.customer_id,
            order_status = EXCLUDED.order_status,
            order_purchase_timestamp = EXCLUDED.order_purchase_timestamp,
            order_approved_at = EXCLUDED.order_approved_at,
            order_delivered_carrier_date = EXCLUDED.order_delivered_carrier_date,
            order_delivered_customer_date = EXCLUDED.order_delivered_customer_date,
            order_estimated_delivery_date = EXCLUDED.order_estimated_delivery_date,
            order_year = EXCLUDED.order_year,
            order_month = EXCLUDED.order_month,
            order_month_name = EXCLUDED.order_month_name,
            order_date = EXCLUDED.order_date,
            order_day = EXCLUDED.order_day,
            order_day_of_week = EXCLUDED.order_day_of_week,
            delivery_days = EXCLUDED.delivery_days,
            estimated_delivery_days = EXCLUDED.estimated_delivery_days;
    """
    execute_values(cur, query, rows, page_size=5000)
    conn.commit()
    cur.close()
    load_time = round(time.time() - start_time, 2)
    return read_count, len(rows), 0, load_time


def load_recommendations(conn):
    """Load recommendations table from recommendations.csv."""
    filepath = os.path.join(BASE_DIR, "results", "recommendation_engine", "recommendations.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing file: {filepath}")

    start_time = time.time()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE recommendations;")

    rows = []
    read_count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            read_count += 1
            rows.append((
                parse_str(r.get("customer_id")),
                parse_int(r.get("rank")),
                parse_str(r.get("product_id")),
                parse_str(r.get("product_category")),
                parse_float(r.get("recommendation_score")),
                parse_float(r.get("apriori_score")),
                parse_float(r.get("similarity_score")),
                parse_float(r.get("popularity_score")),
                parse_str(r.get("recommendation_source"))
            ))

    query = """
        INSERT INTO recommendations (
            customer_id, rank, product_id, product_category,
            recommendation_score, apriori_score, similarity_score,
            popularity_score, recommendation_source
        ) VALUES %s;
    """
    execute_values(cur, query, rows, page_size=5000)
    conn.commit()
    cur.close()
    load_time = round(time.time() - start_time, 2)
    return read_count, len(rows), 0, load_time


def load_association_rules(conn):
    """Load association rules table from association_rules.csv."""
    filepath = os.path.join(BASE_DIR, "results", "apriori", "association_rules.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing file: {filepath}")

    start_time = time.time()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE association_rules;")

    rows = []
    read_count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            read_count += 1
            rows.append((
                parse_str(r.get("antecedent")),
                parse_str(r.get("antecedent_categories")),
                parse_str(r.get("consequent")),
                parse_str(r.get("consequent_categories")),
                parse_float(r.get("antecedent_support")),
                parse_float(r.get("consequent_support")),
                parse_float(r.get("support")),
                parse_int(r.get("support_count")),
                parse_float(r.get("confidence")),
                parse_float(r.get("lift"))
            ))

    query = """
        INSERT INTO association_rules (
            antecedent, antecedent_categories, consequent,
            consequent_categories, antecedent_support, consequent_support,
            support, support_count, confidence, lift
        ) VALUES %s;
    """
    execute_values(cur, query, rows, page_size=100)
    conn.commit()
    cur.close()
    load_time = round(time.time() - start_time, 2)
    return read_count, len(rows), 0, load_time


def load_analytics(conn):
    """Load analytics table from analytics.csv."""
    filepath = os.path.join(BASE_DIR, "data", "processed", "analytics.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing file: {filepath}")

    start_time = time.time()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE analytics;")

    rows = []
    read_count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            read_count += 1
            rows.append((
                parse_str(r.get("order_id")),
                parse_int(r.get("order_item_id")),
                parse_str(r.get("product_id")),
                parse_str(r.get("seller_id")),
                parse_timestamp(r.get("shipping_limit_date")),
                parse_float(r.get("price")),
                parse_float(r.get("freight_value")),
                parse_float(r.get("total_item_value")),
                parse_str(r.get("customer_id")),
                parse_str(r.get("order_status")),
                parse_timestamp(r.get("order_purchase_timestamp")),
                parse_timestamp(r.get("order_approved_at")),
                parse_timestamp(r.get("order_delivered_carrier_date")),
                parse_timestamp(r.get("order_delivered_customer_date")),
                parse_timestamp(r.get("order_estimated_delivery_date")),
                parse_int(r.get("order_year")),
                parse_int(r.get("order_month")),
                parse_str(r.get("order_month_name")),
                parse_date(r.get("order_date")),
                parse_int(r.get("order_day")),
                parse_str(r.get("order_day_of_week")),
                parse_float(r.get("delivery_days")),
                parse_float(r.get("estimated_delivery_days")),
                parse_str(r.get("product_category_name_english")),
                parse_str(r.get("customer_unique_id")),
                parse_str(r.get("customer_city")),
                parse_str(r.get("customer_state"))
            ))

    query = """
        INSERT INTO analytics (
            order_id, order_item_id, product_id, seller_id, shipping_limit_date,
            price, freight_value, total_item_value, customer_id, order_status,
            order_purchase_timestamp, order_approved_at,
            order_delivered_carrier_date, order_delivered_customer_date,
            order_estimated_delivery_date, order_year, order_month,
            order_month_name, order_date, order_day, order_day_of_week,
            delivery_days, estimated_delivery_days,
            product_category_name_english, customer_unique_id,
            customer_city, customer_state
        ) VALUES %s;
    """
    execute_values(cur, query, rows, page_size=5000)
    conn.commit()
    cur.close()
    load_time = round(time.time() - start_time, 2)
    return read_count, len(rows), 0, load_time


# =====================================================================
# MAIN RUNNER
# =====================================================================

def main():
    total_start_time = time.time()
    print("==========================================")
    print("SHOPLYTICS: POSTGRESQL DATA LOADER")
    print("==========================================")

    # 1. Ensure shoplytics database exists
    try:
        ensure_database_exists()
    except Exception as e:
        print(f"\n[ERROR] Could not connect to PostgreSQL server: {e}")
        print("Please ensure the PostgreSQL service is running.")
        sys.exit(1)

    # 2. Connect to shoplytics
    conn = get_db_connection()
    create_tables(conn)

    # 3. Load all tables
    summary_records = []
    table_loaders = [
        ("customer_segments", load_customer_segments),
        ("cluster_profiles", load_cluster_profiles),
        ("customers", load_customers),
        ("products", load_products),
        ("orders", load_orders),
        ("recommendations", load_recommendations),
        ("association_rules", load_association_rules),
        ("analytics", load_analytics)
    ]

    table_row_counts = {}

    for tname, loader_fn in table_loaders:
        print(f"Loading table '{tname}'...")
        try:
            read_cnt, ins_cnt, skip_cnt, elapsed = loader_fn(conn)
            print(f"  -> Read: {read_cnt:,}, Inserted: {ins_cnt:,}, Skipped: {skip_cnt:,} ({elapsed}s)")
            summary_records.append({
                "table": tname,
                "row_count": ins_cnt,
                "load_status": "SUCCESS",
                "load_time_seconds": elapsed
            })
            table_row_counts[tname] = ins_cnt
        except Exception as e:
            print(f"  -> [FAILED] Error loading {tname}: {e}")
            summary_records.append({
                "table": tname,
                "row_count": 0,
                "load_status": f"FAILED: {e}",
                "load_time_seconds": 0.0
            })
            table_row_counts[tname] = 0

    conn.close()

    total_load_time = round(time.time() - total_start_time, 2)

    # 4. Save postgresql_summary.csv
    summary_path = os.path.join(RESULTS_DIR, "postgresql_summary.csv")
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["table", "row_count", "load_status", "load_time_seconds"])
        writer.writeheader()
        writer.writerows(summary_records)
    print(f"\nSummary report saved to: {summary_path}")

    # 5. Print final formatted verification banner
    print("\n==========================================")
    print("SHOPLYTICS POSTGRESQL")
    print("==========================================")
    print(f"\nDatabase:\n{PGDATABASE}\n")
    for tname in ["customers", "products", "orders", "analytics", "customer_segments", "cluster_profiles", "recommendations", "association_rules"]:
        print(f"{tname:<20}: {table_row_counts.get(tname, 0):,}")
    print("\nPostgreSQL connection:")
    print("SUCCESS")
    print(f"\nTotal elapsed time: {total_load_time}s")
    print("==========================================")


if __name__ == "__main__":
    main()

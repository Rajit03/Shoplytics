# Shoplytics PostgreSQL Database Layer

## Overview
- **Database**: `shoplytics`
- **DBMS**: PostgreSQL
- **Administration & SQL Tool**: pgAdmin 4
- **Connector**: `psycopg2-binary`
- **Purpose**: Serves as the relational storage and low-latency query layer between Big Data pipelines (Hadoop/Spark) and the FastAPI web backend.

---

## Relational Tables

### 1. `customers`
- **Purpose**: Unique customer summary metrics including spending, orders, freight, and cluster segmentation.
- **Source File**: `data/processed/customer_features.csv`
- **Primary Key**: `customer_unique_id`
- **Indexes**: `idx_customers_cluster`
- **Example Query**:
  ```sql
  SELECT customer_unique_id, total_orders, total_spending, average_order_value, cluster
  FROM customers
  ORDER BY total_spending DESC
  LIMIT 10;
  ```

### 2. `products`
- **Purpose**: Product catalog attributes including dimensions, weight, photos, and localized category names.
- **Source File**: `data/processed/products_clean.csv`
- **Primary Key**: `product_id`
- **Indexes**: `idx_products_category`
- **Example Query**:
  ```sql
  SELECT product_id, product_category_name_english, product_weight_g
  FROM products
  WHERE product_category_name_english = 'health_beauty'
  LIMIT 10;
  ```

### 3. `orders`
- **Purpose**: Order lifecycle transactions, delivery timelines, and time dimensions.
- **Source File**: `data/processed/orders_clean.csv`
- **Primary Key**: `order_id`
- **Indexes**: `idx_orders_customer_id`, `idx_orders_status`, `idx_orders_purchase_timestamp`
- **Example Query**:
  ```sql
  SELECT order_status, COUNT(*) as order_count
  FROM orders
  GROUP BY order_status
  ORDER BY order_count DESC;
  ```

### 4. `analytics`
- **Purpose**: Denormalized line-item analytics dataset combining orders, products, sellers, categories, and delivery metrics for fast dashboard reporting.
- **Source File**: `data/processed/analytics.csv`
- **Primary Key**: `id` (BIGSERIAL)
- **Indexes**: `idx_analytics_order_id`, `idx_analytics_product_id`, `idx_analytics_cust_uid`, `idx_analytics_category`, `idx_analytics_year_month`
- **Example Query**:
  ```sql
  SELECT product_category_name_english, SUM(total_item_value) AS revenue, COUNT(*) AS items_sold
  FROM analytics
  GROUP BY product_category_name_english
  ORDER BY revenue DESC
  LIMIT 10;
  ```

### 5. `customer_segments`
- **Purpose**: K-Means clustering assignment for all 95k+ customers based on spending and order behaviors.
- **Source File**: Spark K-Means output (`results/spark/customer_segments/`)
- **Primary Key**: `customer_unique_id`
- **Indexes**: `idx_cust_segments_cluster`
- **Example Query**:
  ```sql
  SELECT cluster, COUNT(*) AS total_customers, AVG(total_spending) AS avg_spending
  FROM customer_segments
  GROUP BY cluster
  ORDER BY cluster;
  ```

### 6. `cluster_profiles`
- **Purpose**: High-level statistical profiles and boundaries for each K-Means customer cluster.
- **Source File**: Spark K-Means profile output (`results/spark/cluster_profiles/`)
- **Primary Key**: `cluster`
- **Example Query**:
  ```sql
  SELECT cluster, customers, avg_orders, avg_spending, avg_order_value, min_spending, max_spending
  FROM cluster_profiles
  ORDER BY cluster;
  ```

### 7. `recommendations`
- **Purpose**: Top personalized recommendations generated per customer using collaborative and association ranking.
- **Source File**: Recommendation Engine output (`results/recommendation_engine/recommendations.csv`)
- **Primary Key**: `id` (BIGSERIAL)
- **Indexes**: `idx_recs_customer_id`, `idx_recs_rank`, `idx_recs_product_id`
- **Example Query**:
  ```sql
  SELECT r.customer_id, r.rank, r.product_id, r.product_category, r.recommendation_score, r.recommendation_source
  FROM recommendations r
  WHERE r.customer_id = '0f8758e5b1c6c6b2156a9dddce128558'
  ORDER BY r.rank;
  ```

### 8. `association_rules`
- **Purpose**: Frequent product itemset associations mined with the Apriori algorithm.
- **Source File**: Apriori output (`results/apriori/association_rules.csv`)
- **Primary Key**: `id` (BIGSERIAL)
- **Indexes**: `idx_rules_support`, `idx_rules_confidence`, `idx_rules_lift`
- **Example Query**:
  ```sql
  SELECT antecedent, consequent, support, confidence, lift
  FROM association_rules
  ORDER BY lift DESC
  LIMIT 10;
  ```

---

## How to Run

1. **Install Dependencies**:
   ```cmd
   python -m pip install psycopg2-binary
   ```
2. **Configure Credentials in `.env`**:
   ```ini
   PGHOST=localhost
   PGPORT=5432
   PGUSER=postgres
   PGPASSWORD=your_password
   PGDATABASE=shoplytics
   ```
3. **Execute Data Loader**:
   ```cmd
   python database/postgresql_loader.py
   ```
4. **Run Automated Test Queries & Benchmark**:
   ```cmd
   python database/test_queries.py
   ```
5. **Run SQL Queries in pgAdmin**:
   Open pgAdmin 4 -> Connect to `shoplytics` -> Query Tool -> Open `database/test_queries.sql` -> Execute (F5).

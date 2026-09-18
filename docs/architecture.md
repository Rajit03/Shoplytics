# Shoplytics Platform Architecture Documentation 🏛️

## 1. System Overview

**Shoplytics** is an end-to-end distributed Big Data analytics, machine learning, and business intelligence platform designed for large-scale e-commerce operations. It ingests raw transactional data, orchestrates distributed processing jobs via **Hadoop MapReduce** and **Apache Spark**, runs advanced data mining and recommendation algorithms, stores structured dimensional models in an indexed **PostgreSQL** warehouse, serves low-latency REST endpoints via **FastAPI**, and presents interactive analytical dashboards using **React 18**, **Tailwind CSS**, and **Recharts**.

---

## 2. Multi-Tier Architectural Topology

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             1. DATA INGESTION TIER                          │
│     Brazilian E-Commerce (Olist) Datasets (9 CSV Files: Orders, Customers,  │
│         Order Items, Products, Payments, Reviews, Sellers, Geolocation)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           2. DISTRIBUTED STORAGE (HDFS)                     │
│         HDFS Cluster (/shoplytics/raw, /shoplytics/processed, /results)     │
│         Single-Node Local Workstation Deployment (Default Port: 9000)       │
└──────────────────┬──────────────────────────────────────┬───────────────────┘
                   │                                      │
                   ▼                                      ▼
┌──────────────────────────────────────┐  ┌───────────────────────────────────┐
│     3A. HADOOP MAPREDUCE COMPUTING   │  │    3B. APACHE SPARK IN-MEMORY     │
│  - Python Streaming Mappers/Reducers │  │  - PySpark Sales Analytics Engine │
│  - Order Revenue Aggregation Job     │  │  - Spark SQL Multi-Dim Groupings  │
│  - Category Sales Breakdown Job      │  │  - Spark MLlib K-Means Clustering │
│  - Order Status Distribution Job     │  │  - In-Memory Resilient Datasets   │
└──────────────────┬───────────────────┘  └──────────────────┬────────────────┘
                   │                                         │
                   └───────────────────┬─────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         4. ALGORITHM & MINING ENGINES                       │
│  ├── Market Basket Mining:       Apriori Algorithm (Support, Confidence, Lift)
│  ├── Stream Mining:              Flajolet-Martin (Distinct Count), DGIM (Window)
│  ├── Probabilistic Filtering:    Bloom Filter (Configurable Error Rate)
│  ├── Similarity Modeling:        Jaccard & Cosine Customer Purchase Affinity
│  └── Recommendation Engine:      Hybrid (Collaborative Filtering + Profile Match)
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         5. RELATIONAL DATA WAREHOUSE                        │
│                           PostgreSQL 17 Database                            │
│  - 8 Tables: customers, products, orders, analytics, customer_segments,      │
│              cluster_profiles, recommendations, association_rules           │
│  - B-Tree Performance Indexes: Primary keys, foreign keys, timestamps, clusters
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         6. HIGH-PERFORMANCE REST API                        │
│                           FastAPI Serving Backend                           │
│  - Python 3.13 + Uvicorn ASGI Server + SQLAlchemy 2.0 Connection Pooling    │
│  - 8 Resource Routers / 25+ Typed Endpoints with Pydantic v2 Serialization  │
│  - Interactive API Docs: Swagger UI (/docs) and ReDoc (/redoc)              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         7. REACT ANALYTICS DASHBOARD                        │
│                   React 18 + Vite 8 + Tailwind CSS + Recharts               │
│  - 8 Interactive Views: Dashboard, Customers, Customer 360, Products,       │
│                         Orders, Segments, Recommendations, Association Rules│
│  - Responsive KPI Stat Cards, Interactive Visualizations, Dynamic Filters   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Tier-by-Tier Technical Specifications

### Tier 1: Data Ingestion & Cleansing
- **Source**: Olist Brazilian E-Commerce dataset covering 100,000+ orders from 2016 to 2018.
- **Normalization**: Resolves missing localized category mappings, standardizes currency scales (Brazilian Real $R\$$), handles timestamp formats (`YYYY-MM-DD HH:MM:SS`), and builds denormalized line-item datasets (`data/processed/analytics.csv`).

### Tier 2: Distributed File Storage (HDFS)
- **Engine**: Apache Hadoop 3.3.6 HDFS.
- **Storage Strategy**:
  - `/shoplytics/raw/`: Original source data files.
  - `/shoplytics/processed/`: Standardized CSV partitions feeding analytics engines.
  - `/shoplytics/results/`: Distributed output directories containing analytical summaries.

### Tier 3: Distributed Processing (MapReduce & Spark)
1. **Hadoop MapReduce**:
   - Python streaming mappers and reducers executing batch map and reduce sorting tasks.
   - Computes robust baseline order aggregation, revenue totals, and status distributions.
2. **Apache Spark (PySpark & Spark SQL)**:
   - Utilizes Spark DataFrames and Catalyst optimizer for memory-cached analytics.
   - Executes multi-stage aggregations across product categories, monthly sales progressions, and top sellers.
3. **Spark MLlib Clustering**:
   - Assembles multi-feature vectors (`total_spending`, `total_orders`, `average_order_value`, `total_products`).
   - Fits an unsupervised **K-Means** clustering model ($K=4$) to segment customers into actionable behavioural cohorts (High-Value VIPs, Active Regulars, Occasional Shoppers, Single-Purchase Churn Risks).

### Tier 4: Algorithm & Mining Engines
- **Apriori Algorithm**: Discovers frequent item co-occurrences across transaction baskets with configurable minimum support, confidence, and lift thresholds.
- **Hybrid Recommendation Engine**: Generates top-$N$ personalized product recommendations by combining customer purchase histories, category affinity, and cross-sell rules.
- **Stream & Probabilistic Mining**:
  - *Bloom Filter*: Enables ultra-fast membership tests with zero false negatives.
  - *Flajolet-Martin*: Estimates distinct customer and product counts in $O(1)$ auxiliary space.
  - *DGIM Algorithm*: Approximates 1-bit counts within a sliding window in logarithmic memory space.
  - *Cosine & Jaccard*: Measures item-basket and customer-vector similarities for lookalike audiences.

### Tier 5: Relational Storage & Indexing (PostgreSQL 17)
- **Database**: PostgreSQL 17 (`shoplytics`).
- **Relational Tables**:
  1. `customers`: Customer summary metrics and cluster assignments ($N=95,420$).
  2. `products`: Catalog specifications and dimensions ($N=32,951$).
  3. `orders`: Lifecycle transaction timestamps and statuses ($N=99,441$).
  4. `analytics`: Denormalized line-item analytical dataset ($N=112,650$).
  5. `customer_segments`: K-Means cluster classifications ($N=95,420$).
  6. `cluster_profiles`: Statistical summaries of the 4 clusters ($N=4$).
  7. `recommendations`: Top personalized recommendation records ($N=10,000$).
  8. `association_rules`: Mined frequent association rules ($N=91$).
- **Indexing**: Dedicated B-Tree indexes on primary keys, foreign keys, status fields, clusters, and timestamps delivering sub-5ms query response times.

### Tier 6: Serving Layer (FastAPI Backend)
- **Architecture**: Python 3.13 asynchronous REST API framework running on Uvicorn ASGI.
- **ORM & Pooling**: SQLAlchemy 2.0 with connection pooling (`pool_size=25`, `max_overflow=50`).
- **Security & Integrity**: Strict Pydantic v2 schemas and CORS middleware configured for frontend origins.

### Tier 7: Presentation Layer (React + Vite Frontend)
- **Frontend Stack**: React 18, Vite 8 bundler, Tailwind CSS v3, Recharts visualization library, Lucide React icons, Axios client.
- **Key Modules**:
  - **Executive Dashboard**: Real-time KPI counters, revenue area charts, category distribution bars, and recent orders feed.
  - **Customer 360**: Full customer profile with cluster metrics, order histories, and personal recommendations.
  - **Customer Segments**: Visual cluster breakdown, population metrics, and statistical boundaries.
  - **Market Basket Rules**: Dynamic threshold filtering on Apriori co-purchase rules.

---

## 4. Hardware & Deployment Context

> [!NOTE]
> **Single-Node Workstation Deployment**:
> In this implementation, all tiers (HDFS single-node, Spark `local[*]`, PostgreSQL 17, FastAPI, and Vite) operate in a coordinated single-node environment on Windows 11. While the system architecture is natively horizontally scalable for multi-node enterprise Hadoop/Spark clusters, local benchmarking avoids unnecessary network latency during development and evaluation.

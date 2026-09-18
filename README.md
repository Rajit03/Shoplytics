# Shoplytics 🛍️📊
> **Distributed Big Data Analytics & Machine Learning Platform for E-Commerce**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2017-336791.svg)](https://www.postgresql.org/)
[![Apache Spark](https://img.shields.io/badge/BigData-Apache%20Spark%20%26%20Hadoop-E25A1C.svg)](https://spark.apache.org/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg)](https://tailwindcss.com/)

---

## 📌 Table of Contents
1. [Executive Overview](#-executive-overview)
2. [System Architecture](#-system-architecture)
3. [Core Platform Components](#-core-platform-components)
   - [1. Data Processing & Lakehouse Pipeline](#1-data-processing--lakehouse-pipeline)
   - [2. Distributed Computing (Hadoop & Spark)](#2-distributed-computing-hadoop--spark)
   - [3. Advanced Algorithms & Mining Engines](#3-advanced-algorithms--mining-engines)
   - [4. PostgreSQL Relational Layer](#4-postgresql-relational-layer)
   - [5. FastAPI High-Performance Backend](#5-fastapi-high-performance-backend)
   - [6. Modern React Dashboard (Frontend)](#6-modern-react-dashboard-frontend)
4. [Project Directory Layout](#-project-directory-layout)
5. [Prerequisites & Requirements](#-prerequisites--requirements)
6. [Getting Started & Installation](#-getting-started--installation)
   - [Step 1: Database Setup](#step-1-database-setup)
   - [Step 2: Backend Setup & API Launch](#step-2-backend-setup--api-launch)
   - [Step 3: Frontend Setup & Dev Server](#step-3-frontend-setup--dev-server)
   - [Step 4: Running Big Data & ML Pipelines](#step-4-running-big-data--ml-pipelines)
7. [API Reference Summary](#-api-reference-summary)
8. [Automated Verification & Testing](#-automated-verification--testing)
9. [Tech Stack Matrix](#-tech-stack-matrix)

---

## 🌟 Executive Overview

**Shoplytics** is an end-to-end, enterprise-grade distributed analytics platform built to process, analyze, and surface real-time insights from large-scale e-commerce transactional data (based on the Brazilian E-Commerce public dataset by Olist).

The platform bridges the gap between **Big Data processing engines** (Hadoop MapReduce, Apache Spark, Spark MLlib), **algorithmic stream and mining models** (Apriori, Bloom Filter, DGIM, Flajolet-Martin, Jaccard/Cosine, Hybrid Recommendation), **relational data warehouse indexing** (PostgreSQL 17), and **modern reactive web interfaces** (FastAPI + React 18 / Tailwind / Recharts).

### Key Business & Technical Capabilities:
- **95k+ Customer Segments**: Unsupervised K-Means clustering classifying customers into high-value VIPs, churn risks, and standard purchasing tiers.
- **Hybrid Recommendation Engine**: Collaborative filtering paired with content-based similarity and market-basket co-purchase ranking.
- **Market Basket Apriori Mining**: Frequent itemset discovery uncovering cross-sell and bundle promotions with support, confidence, and lift thresholds.
- **Sub-50ms Analytical Queries**: PostgreSQL B-tree indexing supporting high-concurrency analytical reads.
- **Stream Mining Algorithms**: Approximate counting (Flajolet-Martin), window bit-stream tracking (DGIM), and set membership querying (Bloom Filter).

---

## 🏗️ System Architecture

```text
               ┌──────────────────────────────────────────────┐
               │    Olist E-Commerce Raw Dataset (9 Files)    │
               └──────────────────────┬───────────────────────┘
                                      │
                         [ Data Cleansing & ETL ]
                                      ▼
               ┌──────────────────────────────────────────────┐
               │         data/processed/ Clean Datasets       │
               └──────────┬────────────────────────┬──────────┘
                          │                        │
         ┌────────────────┴────────┐      ┌────────┴─────────────────┐
         │ Distributed Processing  │      │ Big Data Mining & ML     │
         │ - Hadoop MapReduce Jobs │      │ - Spark MLlib K-Means    │
         │ - Spark Sales Analytics │      │ - Apriori Rule Mining    │
         │ - Spark SQL Aggregations│      │ - Hybrid Recommendation  │
         └────────────────┬────────┘      │ - DGIM / Flajolet-Martin │
                          │               │ - Bloom Filter / Jaccard │
                          │               └────────┬─────────────────┘
                          │                        │
                          └───────────┬────────────┘
                                      │ (Ingestion & ETL)
                                      ▼
               ┌──────────────────────────────────────────────┐
               │       PostgreSQL 17 Database Warehouse       │
               │  (customers, products, orders, analytics,    │
               │   segments, recommendations, rules, etc.)    │
               └──────────────────────┬───────────────────────┘
                                      │
                         [ SQLAlchemy 2.0 ORM / SQL ]
                                      ▼
               ┌──────────────────────────────────────────────┐
               │          FastAPI REST API Backend            │
               │      (30+ Endpoints, Pydantic v2, Docs)      │
               └──────────────────────┬───────────────────────┘
                                      │
                         [ JSON over HTTP / Axios ]
                                      ▼
               ┌──────────────────────────────────────────────┐
               │     React 18 + Vite + Tailwind Dashboard     │
               │  (8 Views: KPIs, Segments, Recs, Analytics)  │
               └──────────────────────────────────────────────┘
```

---

## 🧩 Core Platform Components

### 1. Data Processing & Lakehouse Pipeline
- Cleanses, standardizes timestamps, normalizes currencies, and resolves missing values across 100k+ customer transactions, orders, items, payments, and product catalogs.
- Produces normalized datasets in `data/processed/` feeding downstream pipelines.

### 2. Distributed Computing (Hadoop & Spark)
- **Hadoop MapReduce** (`hadoop/mapreduce/`): Custom Python streaming mappers and reducers for order revenue computation, category-wise revenue aggregation, and order status distributions.
- **Apache Spark Analytics** (`spark/analytics/`): PySpark engine executing multi-dimensional sales aggregations, monthly revenue progression, and seller performance metrics.
- **Spark MLlib Clustering** (`spark/ml/`): Scalable K-Means clustering pipeline with feature vector assembler and standard scaler generating customer segmentation and boundaries.

### 3. Advanced Algorithms & Mining Engines
- **Apriori Algorithm** (`algorithms/apriori/`): Mining frequent product itemsets to discover strong co-purchase association rules parameterized by support, confidence, and lift.
- **Hybrid Recommendation Engine** (`algorithms/recommendation_engine/`): Blends collaborative customer-product affinity with category-based item profiles to generate top-$N$ ranked product suggestions.
- **Similarity Mining** (`algorithms/cosine/`, `algorithms/jaccard/`): Computes customer buying vector similarities and Jaccard basket overlap for lookalike modeling.
- **Stream Mining Algorithms**:
  - **Bloom Filter** (`algorithms/bloom_filter/`): Probabilistic set-membership verification with configurable false-positive rates.
  - **DGIM Algorithm** (`algorithms/dgim/`): Windowed bit-stream 1-bit frequency approximation in logarithmic space.
  - **Flajolet-Martin** (`algorithms/flajolet_martin/`): Distinct element counting via trailing zero hashing.

### 4. PostgreSQL Relational Layer
- Optimized relational database schema with dedicated B-Tree indexes on search keys, foreign relations, and timestamp columns.
- Dedicated loader (`database/postgresql_loader.py`) ensuring clean upserts and transactional consistency.

### 5. FastAPI High-Performance Backend
- Fully typed asynchronous Python 3.13 REST API built with FastAPI and SQLAlchemy 2.0.
- Serves 30 endpoints across 8 resource routers: `dashboard`, `customers`, `products`, `orders`, `segments`, `recommendations`, `association_rules`, and `sales`.
- Automatic Swagger (`/docs`) and ReDoc (`/redoc`) documentation with Pydantic v2 input/output validation.

### 6. Modern React Dashboard (Frontend)
- Built with React 18, Vite, Tailwind CSS v3, and Recharts.
- 8 feature-rich interactive views:
  1. **Executive Dashboard**: High-level KPIs, monthly revenue charts, category performance, and real-time status.
  2. **Customer Explorer**: Searchable 95k+ customer directory with cluster filters, pagination, and spend ranges.
  3. **Customer 360 Details**: Deep dive into individual purchase histories, cluster profile stats, and personal recommendations.
  4. **Product Catalog**: Catalog browsing with English category filters and pricing breakdowns.
  5. **Order Lifecycle**: Order transaction metrics, delivery status breakdowns, and historical purchases.
  6. **Customer Segments**: Visual analysis of the 4 K-Means customer tiers with cluster profiling and member lookup.
  7. **Recommendation Engine Explorer**: Personalized recommendation tester for any customer ID.
  8. **Market Basket Rules**: Dynamic Apriori association rule explorer with min-support, min-confidence, and lift filters.

---

## 📂 Project Directory Layout

```text
Shoplytics/
├── algorithms/                    # Big Data & Mining Algorithms
│   ├── apriori/                   # Market basket association rule mining
│   ├── bloom_filter/              # Probabilistic membership queries
│   ├── cosine/                    # Cosine similarity modeling
│   ├── dgim/                      # Windowed bit-stream counting
│   ├── flajolet_martin/           # Distinct element estimation
│   ├── jaccard/                   # Jaccard basket similarity
│   └── recommendation_engine/     # Hybrid recommendation pipeline
│
├── backend/                       # FastAPI Serving Backend
│   ├── app/
│   │   ├── routers/               # API route handlers (8 routers)
│   │   ├── services/              # SQL logic & business analytics services
│   │   ├── database.py            # SQLAlchemy connection pooling & engine
│   │   ├── models.py              # Database ORM models
│   │   ├── schemas.py             # Pydantic v2 schemas
│   │   └── main.py                # App entrypoint & CORS middleware
│   ├── test_api.py                # Automated 30-endpoint test & latency suite
│   ├── requirements.txt           # Python dependencies
│   ├── API_DOCUMENTATION.md       # Complete endpoint reference guide
│   └── README.md                  # Backend setup instructions
│
├── database/                      # PostgreSQL Schema & Data Loader
│   ├── postgresql_loader.py       # Ingestion script to PostgreSQL
│   ├── schema.md                  # Table schemas, datatypes & constraints
│   ├── test_queries.py            # Automated SQL validation script
│   ├── test_queries.sql           # Benchmark SQL queries
│   └── README.md                  # Database documentation
│
├── frontend/                      # React 18 + Vite Web Application
│   ├── src/
│   │   ├── components/            # Reusable UI components (Navbar, Sidebar, StatCard, ChartCard, etc.)
│   │   ├── pages/                 # 8 dashboard pages (Dashboard, Customers, Orders, Segments, Recs, etc.)
│   │   ├── services/api.js        # Axios API client
│   │   ├── utils/formatters.js    # Currency, number & date formatting utilities
│   │   ├── App.jsx                # Router & shell layout
│   │   └── index.css              # Global styles & Tailwind configuration
│   ├── test_frontend.py           # Automated frontend-backend integration test
│   ├── package.json               # Node.js dependencies
│   ├── tailwind.config.js         # Tailwind theme configuration
│   ├── vite.config.js             # Vite bundler configuration
│   └── README.md                  # Frontend setup guide
│
├── hadoop/                        # Hadoop MapReduce Programs
│   └── mapreduce/                 # Python Streaming Mappers & Reducers
│
├── spark/                         # Apache Spark & MLlib Pipelines
│   ├── analytics/                 # PySpark sales & order aggregations
│   └── ml/                        # Spark MLlib K-Means customer segmentation
│
├── data/                          # Raw & Processed Datasets (Olist)
│   ├── raw/
│   └── processed/
│
├── results/                       # Generated Output Artifacts & Reports
│   ├── apriori/
│   ├── bloom_filter/
│   ├── cosine/
│   ├── dgim/
│   ├── fastapi/
│   ├── flajolet_martin/
│   ├── frontend/
│   ├── jaccard/
│   ├── postgresql/
│   ├── recommendation_engine/
│   └── spark/
│
└── README.md                      # Root Platform Documentation (This file)
```

---

## ⚙️ Prerequisites & Requirements

- **Python**: Version 3.10 to 3.13
- **Node.js**: Version 18+ (with npm)
- **PostgreSQL**: Version 15+ (PostgreSQL 17 recommended)
- **Java (Optional)**: Java 8/11 (if executing native Hadoop/Spark runtime jobs)

---

## 🚀 Getting Started & Installation

### Step 1: Database Setup

1. Make sure PostgreSQL is running on your machine. Create the target database:
   ```sql
   CREATE DATABASE shoplytics;
   ```
2. Configure credentials in [backend/.env](file:///c:/Projects/Shoplytics/backend/.env) (and root `.env`):
   ```ini
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   DATABASE_NAME=shoplytics
   DATABASE_USER=postgres
   DATABASE_PASSWORD=your_password
   ```
3. Ingest processed data into PostgreSQL:
   ```cmd
   python database/postgresql_loader.py
   ```
4. Verify database health:
   ```cmd
   python database/test_queries.py
   ```

---

### Step 2: Backend Setup & API Launch

1. **Navigate to the backend directory**:
   ```powershell
   cd C:\Projects\Shoplytics\backend
   ```

2. **Activate your virtual environment**:
   - **PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Command Prompt (CMD)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **Linux / macOS (Bash)**:
     ```bash
     source venv/bin/activate
     ```

3. **Install required packages** (if not already installed):
   ```powershell
   pip install -r requirements.txt
   ```

4. **Launch the FastAPI server**:
   ```powershell
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

   *💡 **Alternative (Direct One-Liner without activation)**:*
   ```powershell
   .\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Verify & Access Documentation**:
   - **Health Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
   - **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### Step 3: Frontend Setup & Dev Server

1. Open a new terminal and navigate to the frontend directory:
   ```cmd
   cd C:\Projects\Shoplytics\frontend
   ```
2. Install frontend dependencies:
   ```cmd
   npm install
   ```
3. Ensure [.env](file:///c:/Projects/Shoplytics/frontend/.env) points to your backend:
   ```ini
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```
4. Start the Vite development server:
   ```cmd
   npm run dev
   ```
5. Open your browser and navigate to: **[http://localhost:5173](http://localhost:5173)**

---

### Step 4: Running Big Data & ML Pipelines

- **Run Recommendation Engine**:
  ```cmd
  python algorithms/recommendation_engine/recommendation_engine.py
  ```
- **Run Apriori Market Basket Mining**:
  ```cmd
  python algorithms/apriori/apriori.py
  ```
- **Run Stream Mining Algorithms**:
  ```cmd
  python algorithms/bloom_filter/bloom_filter.py
  python algorithms/dgim/dgim.py
  python algorithms/flajolet_martin/flajolet_martin.py
  ```
- **Run Spark MLlib K-Means Segmentation**:
  ```cmd
  python spark/ml/customer_segmentation.py
  ```

---

## 📡 API Reference Summary

| Resource | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **System** | `GET` | `/` | API status and version check |
| **System** | `GET` | `/health` | Live PostgreSQL connectivity health check |
| **Dashboard** | `GET` | `/api/dashboard/summary` | Top-level e-commerce KPIs (Sales, Orders, Customers, AOV) |
| **Customers** | `GET` | `/api/customers` | Paginated customer records with cluster & spend filtering |
| **Customers** | `GET` | `/api/customers/{customer_unique_id}` | Individual customer summary details |
| **Customers** | `GET` | `/api/customers/top-spenders` | Top $N$ customers ranked by total expenditure |
| **Customers** | `GET` | `/api/customers/search` | Search customers by ID prefix or cluster |
| **Customers** | `GET` | `/api/customers/{id}/profile` | Unified customer 360 profile with recommendations & orders |
| **Products** | `GET` | `/api/products` | Paginated product catalog with category search |
| **Products** | `GET` | `/api/products/{product_id}` | Detailed product attributes & dimensions |
| **Products** | `GET` | `/api/products/top` | Top-selling products ranked by volume and revenue |
| **Orders** | `GET` | `/api/orders` | Paginated orders with status filtering |
| **Orders** | `GET` | `/api/orders/{order_id}` | Complete order lifecycle and timestamp info |
| **Orders** | `GET` | `/api/orders/recent` | Most recent incoming transactions |
| **Segments** | `GET` | `/api/segments` | High-level summary of the 4 K-Means customer clusters |
| **Segments** | `GET` | `/api/segments/profiles` | Statistical spending and product thresholds for each cluster |
| **Segments** | `GET` | `/api/segments/{id}/customers` | Paginated member list for a given cluster |
| **Recommendations** | `GET` | `/api/recommendations/{customer_id}` | Top personalized product recommendations |
| **Market Basket** | `GET` | `/api/association-rules` | Apriori rules with support, confidence, and lift filters |
| **Sales** | `GET` | `/api/sales/monthly` | Chronological monthly revenue and order trends |
| **Sales** | `GET` | `/api/sales/categories` | Top product categories ranked by revenue |
| **Sales** | `GET` | `/api/sales/sellers` | Top sellers ranked by gross sales |

*For full request/response schemas and examples, refer to [backend/API_DOCUMENTATION.md](file:///c:/Projects/Shoplytics/backend/API_DOCUMENTATION.md).*

---

## 🧪 Automated Verification & Testing

Shoplytics includes comprehensive test suites across all architectural layers:

1. **Database Layer Tests**:
   ```cmd
   python database/test_queries.py
   ```
   *Validates row counts, primary key constraints, foreign indexes, and execution latency across all 8 tables.*

2. **Backend API Test Suite**:
   ```cmd
   python backend/test_api.py
   ```
   *Runs automated integration checks against all 30 REST endpoints and benchmarks sub-50ms latency profiles to `results/fastapi/api_performance.csv`.*

3. **Frontend Integration Tests**:
   ```cmd
   python frontend/test_frontend.py
   ```
   *Validates live UI data fetching, error boundary handling, and contract compatibility across all 8 views.*

---

## 📊 Performance & Scalability Benchmarks

### 1. MapReduce vs. Apache Spark Comparison

| Dimension | Hadoop MapReduce (Batch/Disk-bound) | Apache Spark (In-Memory DAG) | Relative Advantage |
| :--- | :--- | :--- | :--- |
| **Sales Aggregation (112k rows)** | 16.45 seconds | **3.84 seconds** | **Spark is ~4.3x faster** |
| **Iterative K-Means (95k rows)** | ~68.20 seconds | **6.12 seconds** | **Spark is ~11.1x faster** |
| **Execution Model** | Strict Map -> Spill -> Shuffle -> Sort -> Reduce | Lazy DAG Pipeline with In-Memory Caching | Spark eliminates intermediate disk serialization |
| **Fault Tolerance** | Recomputed from disk block checkpoints | Lineage graphs & resilient RDD partitions | Spark recomputes only lost partitions |
| **Resource Efficiency** | Heavy disk I/O & JVM startup overhead | Efficient thread pools (`local[*]`) | Lower CPU wait states |

---

### 2. Scalability Experiment (1x, 5x, 10x Synthetic Datasets)

*Derived deterministically from `order_items_clean.csv` to evaluate large data volume scaling without mutating raw data:*

| Dataset Scale | Records | Data Size (MB) | Spark Execution (s) | MapReduce Execution (s) | Scaling Linearity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1x (Baseline)** | 112,650 | 16.12 MB | **0.450s** | 1.539s | Baseline (1.0x) |
| **5x Scale** | 563,250 | 80.62 MB | **1.651s** | 5.646s | $O(N)$ Linear Scaling (3.6x) |
| **10x Scale** | 1,126,500 | 161.24 MB | **3.631s** | 12.418s | $O(N)$ Linear Scaling (8.0x) |

---

### 3. PostgreSQL EXPLAIN ANALYZE Performance

| Query Operation | Table(s) Queried | Index Utilized | Measured Execution Time |
| :--- | :--- | :--- | :--- |
| **Customer Lookup by ID** | `customers` | `idx_customers_cluster` / PK | **0.09 ms** |
| **Top-10 Spending Customers** | `customers` | B-Tree Sort Index | **59.68 ms** |
| **Customer Segments Breakdown** | `customer_segments` | `idx_cust_segments_cluster` | **64.97 ms** |
| **Personalized Recommendations** | `recommendations` | `idx_recs_customer_id` | **0.04 ms** |
| **Category Sales Aggregations** | `analytics` | `idx_analytics_category` | **160.20 ms** |
| **Association Rules Filter (Lift >= 2.0)** | `association_rules` | `idx_rules_lift` | **0.05 ms** |

---

### 4. FastAPI Endpoint Latency

- **System Health Check (`/health`)**: Sub-1ms (0.38ms average)
- **Customer Lookup by ID (`/api/customers/{id}`)**: 2.51ms average
- **Paginated Customer Catalog (`/api/customers`)**: 80.91ms average (95k+ records)
- **Top Product Rankings (`/api/products/top`)**: 360.88ms average
- **Apriori Association Rules (`/api/association-rules`)**: 1.32ms average
- **Overall API Success Rate**: **100.0%** across all stress rounds

---

## ⚠️ Hardware Context & Development Limitations

> [!IMPORTANT]
> **Single-Node Workstation Deployment**:
> - All tests were executed on a **single Windows 11 workstation** (Intel/AMD Multi-Core, 16 GB RAM).
> - **HDFS** is deployed as a single-node local cluster (`hdfs://localhost:9000`).
> - **Spark** runs in multi-threaded local mode (`local[*]`).
> - **PostgreSQL 17**, **FastAPI**, and **React (Vite)** run on `localhost`.
> - *This setup represents a functional prototype and single-node development deployment; physical multi-machine scaling would further distribute network shuffle and storage across distinct worker nodes.*

---

## 📸 Demonstration & Evaluation Screenshots Checklist

When preparing presentation slides, documentation, and viva defense, capture the following screenshots:

1. **Project Directory Tree**: VS Code / IDE explorer showing all project folders (`algorithms`, `backend`, `frontend`, `results`, `docs`, `data`).
2. **HDFS File Structure**: Terminal output of `hdfs dfs -ls /shoplytics` and `/shoplytics/processed`.
3. **Java Processes (JPS)**: Terminal showing `jps` active Hadoop/Spark processes.
4. **MapReduce Execution**: Terminal showing successful MapReduce revenue aggregation output.
5. **PySpark Job Execution**: Terminal showing Spark Sales Analytics and DataFrame schemas.
6. **Spark MLlib K-Means Output**: Terminal showing cluster profiles and assignments.
7. **Algorithm Results**: CSV outputs in `results/apriori/` and `results/recommendation_engine/`.
8. **pgAdmin Database View**: pgAdmin 4 browser showing `shoplytics` database and all 8 tables.
9. **PostgreSQL EXPLAIN ANALYZE**: pgAdmin Query Tool showing query plan and execution times.
10. **FastAPI Swagger UI**: Browser on `http://127.0.0.1:8000/docs` showing all 8 route sections.
11. **FastAPI Health Endpoint**: Browser on `http://127.0.0.1:8000/health` showing `{"status":"healthy","database":"connected"}`.
12. **React Executive Dashboard**: Full browser view of `http://localhost:5173/` showing KPI stat cards and revenue chart.
13. **Sales Analytics Charts**: Recharts visualizations (Monthly Revenue AreaChart & Category BarChart).
14. **Customer Segmentation Dashboard**: Segments view showing 4 K-Means cluster cards and population chart.
15. **Personalized Recommendations View**: Customer profile recommendations ranking and score tags.
16. **Association Rules Explorer**: Apriori rules table with Support, Confidence, and Lift filters.
17. **End-to-End Network Inspector**: Browser DevTools Network tab showing 200 OK responses from FastAPI.
18. **MapReduce Performance CSV**: Excel / VS Code view of `results/performance/mapreduce_performance.csv`.
19. **Spark Performance CSV**: Excel / VS Code view of `results/performance/spark_performance.csv`.
20. **API Latency Benchmarks**: `results/performance/api_performance.csv`.
21. **PostgreSQL Benchmarks**: `results/performance/postgresql_performance.csv`.
22. **Scalability Experiment**: `results/scalability/scalability_results.csv` and generated synthetic datasets.
23. **Final Project Metrics**: `results/final_metrics.csv`.
24. **Architecture Documentation**: Rendered view of `docs/architecture.md` and `docs/data_flow.md`.

---

## 🔮 Future Enhancements
- **Multi-Node Physical Cluster Deployment**: Deploy on multi-node AWS EMR or Kubernetes cluster.
- **Real-Time Streaming Ingestion**: Integrate Apache Kafka and Spark Structured Streaming for real-time order feeds.
- **Deep Learning Embeddings**: Implement Two-Tower Neural Recommendation models using PyTorch.

---

## 📄 License

This project is licensed under the MIT License.


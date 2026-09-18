# Shoplytics FastAPI Backend

## 1. Overview
The **Shoplytics Backend** is a high-performance REST API built with **FastAPI** and **PostgreSQL 17**. It acts as the operational serving layer that exposes Big Data analytical findings, K-Means customer segmentation, Apriori market basket association rules, and hybrid product recommendations to frontend consumers and analytical dashboards.

---

## 2. Technology Stack
- **Framework**: FastAPI (Python 3.13)
- **ASGI Server**: Uvicorn
- **ORM & Connection Pooling**: SQLAlchemy 2.0
- **Database**: PostgreSQL 17 (`shoplytics`)
- **Validation & Serialization**: Pydantic v2
- **Testing & Benchmarking**: Requests & CSV Logger

---

## 3. Directory Structure
```text
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # App setup, CORS, lifespan, exception handlers
│   ├── database.py                 # Engine & Session factory
│   ├── models.py                   # SQLAlchemy ORM models (8 tables)
│   ├── schemas.py                  # Pydantic v2 schemas & Generic pagination
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── dashboard.py            # /api/dashboard/summary
│   │   ├── customers.py            # /api/customers/*
│   │   ├── products.py             # /api/products/*
│   │   ├── orders.py               # /api/orders/*
│   │   ├── segments.py             # /api/segments/*
│   │   ├── recommendations.py      # /api/recommendations/*
│   │   ├── association_rules.py    # /api/association-rules/*
│   │   └── sales.py                # /api/sales/*
│   │
│   └── services/
│       ├── __init__.py
│       └── analytics_service.py    # Parameterized SQL & business logic layer
│
├── venv/                           # Isolated Python Virtual Environment
├── requirements.txt                # Pinned dependencies
├── .env                            # Database credentials
├── .gitignore                      # Git exclusion rules
├── test_api.py                     # Automated testing & latency benchmarking
├── README.md                       # Backend overview & guide
└── API_DOCUMENTATION.md            # Complete API reference
```

---

## 4. Setup & Running

### 1. Activate Virtual Environment
- **PowerShell**:
  ```powershell
  cd C:\Projects\Shoplytics\backend
  .\venv\Scripts\Activate.ps1
  ```
- **Command Prompt (CMD)**:
  ```cmd
  cd C:\Projects\Shoplytics\backend
  venv\Scripts\activate.bat
  ```
- **Linux / macOS (Bash)**:
  ```bash
  source venv/bin/activate
  ```

### 2. Configure Environment (`.env`)
```ini
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=shoplytics
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
```

### 3. Launch Development Server
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

*💡 **Direct One-Liner (No manual activation needed)**:*
```powershell
.\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Interactive Documentation
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 5. Automated Testing
Run the automated test runner to test all 30 endpoints and benchmark latency:
```cmd
python test_api.py
```
Outputs are written to `results/fastapi/api_performance.csv` and `results/fastapi/api_test_results.txt`.

# Shoplytics React + Vite + Tailwind CSS Frontend

## 1. Overview
The **Shoplytics Frontend** is a distributed e-commerce analytics dashboard built with **React 18**, **Vite**, **Tailwind CSS**, and **Recharts**. It communicates with the **FastAPI** backend to render interactive visualizations, K-Means customer segmentation profiles, hybrid product recommendations, Apriori association rules, and comprehensive order lifecycle data.

---

## 2. Technology Stack
- **UI Framework**: React 18
- **Build Tool**: Vite v8
- **Styling**: Tailwind CSS v3 with PostCSS & Autoprefixer
- **Charts & Visualizations**: Recharts
- **Icons**: Lucide React
- **Routing**: React Router DOM v7
- **HTTP Client**: Axios

---

## 3. Directory Structure
```text
frontend/
│
├── src/
│   ├── components/
│   │   ├── Navbar.jsx              # Top navigation with live status badge & clock
│   │   ├── Sidebar.jsx             # Drawer navigation with active routes & Lucide icons
│   │   ├── StatCard.jsx            # KPI metric cards with trends
│   │   ├── ChartCard.jsx           # Responsive Recharts container
│   │   ├── DataTable.jsx           # Reusable paginated data table
│   │   ├── Loading.jsx             # Animated loading state
│   │   ├── ErrorMessage.jsx        # Error alert banner with retry
│   │   └── Badge.jsx               # Segment and status tags
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx           # Executive overview & revenue trends
│   │   ├── Customers.jsx           # Paginated 95k+ customer list & search
│   │   ├── CustomerDetails.jsx     # Profile, cluster stats, orders, & recommendations
│   │   ├── Products.jsx            # Product catalog & category filtering
│   │   ├── Orders.jsx              # Order lifecycle transactions & delivery metrics
│   │   ├── Segments.jsx            # 4-Cluster K-Means breakdown & member lookup
│   │   ├── Recommendations.jsx     # Hybrid recommendation engine explorer
│   │   └── AssociationRules.jsx    # Apriori market basket co-purchase rules
│   │
│   ├── services/
│   │   └── api.js                  # Axios client matching FastAPI routes
│   │
│   ├── hooks/
│   │   └── useApi.js               # Data-fetching custom hook
│   │
│   ├── utils/
│   │   └── formatters.js           # Brazilian Real (R$), compact number, & date formatters
│   │
│   ├── App.jsx                     # Layout shell & Route definitions
│   ├── main.jsx                    # React bootstrap
│   └── index.css                   # Custom theme & Tailwind directives
│
├── .env                            # VITE_API_BASE_URL=http://127.0.0.1:8000
├── .gitignore                      # Ignore node_modules, dist, .env
├── package.json                    # Project dependencies
├── tailwind.config.js              # Tailwind configuration
├── vite.config.js                  # Vite configuration
└── test_frontend.py                # Automated integration validator
```

---

## 4. Setup & Running

### 1. Install Dependencies
```cmd
cd C:\Projects\Shoplytics\frontend
npm install
```

### 2. Configure Environment (`.env`)
```ini
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 3. Launch Development Server
```cmd
npm run dev
```
Accessible at: **http://localhost:5173** (or http://127.0.0.1:5173).

### 4. Build for Production
```cmd
npm run build
```

---

## 5. Automated Validation
Run the integration validation script to test all 8 views against the live backend:
```cmd
python test_frontend.py
```
Outputs are saved to `results/frontend/frontend_test_results.txt` and `results/frontend/frontend_api_test.csv`.

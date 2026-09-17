# Shoplytics API Documentation

Complete reference of all REST API endpoints provided by the Shoplytics backend.

---

## 1. System Endpoints

### `GET /`
- **Purpose**: Root status check.
- **Response**:
  ```json
  {
    "message": "Shoplytics API is running",
    "version": "1.0.0"
  }
  ```

### `GET /health`
- **Purpose**: Live PostgreSQL connectivity health check.
- **Response**:
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "timestamp": "2026-09-18T00:50:00.000Z"
  }
  ```

---

## 2. Dashboard Endpoints

### `GET /api/dashboard/summary`
- **Purpose**: Top-level e-commerce KPI summary.
- **Response**:
  ```json
  {
    "total_customers": 95420,
    "total_orders": 98666,
    "total_products": 32951,
    "total_sales": 15843553.24,
    "total_freight": 2251909.54,
    "average_order_value": 160.58,
    "delivered_orders": 96478,
    "cancelled_orders": 625,
    "active_categories": 71,
    "total_clusters": 4
  }
  ```

---

## 3. Customers Endpoints

### `GET /api/customers`
- **Purpose**: Retrieve paginated customer list.
- **Query Parameters**:
  - `page` (int, default=1)
  - `page_size` (int, default=20)
  - `cluster` (int, optional)
  - `min_spending` (float, optional)
  - `max_spending` (float, optional)
- **Response**:
  ```json
  {
    "page": 1,
    "page_size": 20,
    "total": 95420,
    "total_pages": 4771,
    "data": [
      {
        "customer_unique_id": "0a0a92112bd4c708ca5fde585afaa872",
        "total_orders": 1,
        "total_spending": 13440.0,
        "total_freight": 198.72,
        "total_products": 8,
        "average_order_value": 13440.0,
        "cluster": 2
      }
    ]
  }
  ```

### `GET /api/customers/{customer_unique_id}`
- **Purpose**: Retrieve customer record by ID.

### `GET /api/customers/top-spenders`
- **Purpose**: Retrieve top $N$ customers ranked by total spending.
- **Query Parameters**: `limit` (int, default=10)

### `GET /api/customers/search`
- **Purpose**: Search customers by ID prefix or cluster.
- **Query Parameters**: `query` (str), `cluster` (int), `limit` (int)

### `GET /api/customers/{customer_unique_id}/profile`
- **Purpose**: Unified customer profile with K-Means cluster info, order history, and product recommendations.

---

## 4. Products Endpoints

### `GET /api/products`
- **Purpose**: Paginated product catalog.
- **Query Parameters**: `page` (int), `page_size` (int), `category` (str)

### `GET /api/products/{product_id}`
- **Purpose**: Product physical dimensions and category metadata.

### `GET /api/products/category/{category}`
- **Purpose**: Filter products by English category name.

### `GET /api/products/top`
- **Purpose**: Top selling products ranked by revenue and units sold.
- **Query Parameters**: `limit` (int, default=10)

---

## 5. Orders Endpoints

### `GET /api/orders`
- **Purpose**: Paginated orders list.
- **Query Parameters**: `page` (int), `page_size` (int), `status` (str)

### `GET /api/orders/{order_id}`
- **Purpose**: Order transaction details and lifecycle timestamps.

### `GET /api/orders/status/{status}`
- **Purpose**: Orders filtered by specific status (`delivered`, `shipped`, `canceled`).

### `GET /api/orders/recent`
- **Purpose**: Most recent orders by purchase timestamp.

---

## 6. Customer Segments Endpoints

### `GET /api/segments`
- **Purpose**: Population and average spending overview for all 4 clusters.

### `GET /api/segments/profiles`
- **Purpose**: Statistical boundaries (min/max/avg spending, avg products) for K-Means clusters.

### `GET /api/segments/{cluster_id}`
- **Purpose**: Specific cluster profile details.

### `GET /api/segments/{cluster_id}/customers`
- **Purpose**: Paginated customers in a specific cluster.

---

## 7. Recommendations Endpoints

### `GET /api/recommendations/{customer_id}`
- **Purpose**: Personalized recommendations for a customer sorted by rank.
- **Query Parameters**: `limit` (int, default=10)

### `GET /api/recommendations`
- **Purpose**: Paginated recommendations list with optional filters.
- **Query Parameters**: `customer_id` (str), `product_id` (str), `source` (str)

---

## 8. Association Rules Endpoints

### `GET /api/association-rules`
- **Purpose**: Apriori market basket rules with threshold filters.
- **Query Parameters**: `limit` (int), `min_support` (float), `min_confidence` (float), `min_lift` (float)

### `GET /api/association-rules/top`
- **Purpose**: Top association rules sorted by lift.

---

## 9. Sales & Analytics Endpoints

### `GET /api/sales/summary`
- **Purpose**: Total sales, net product revenue, freight, and orders count.

### `GET /api/sales/monthly`
- **Purpose**: Chronological monthly revenue and order volume trends.

### `GET /api/sales/categories`
- **Purpose**: Product categories ranked by sales revenue.

### `GET /api/sales/products`
- **Purpose**: Top selling products by revenue.

### `GET /api/sales/sellers`
- **Purpose**: Top sellers by revenue.

### `GET /api/sales/order-status`
- **Purpose**: Order status distribution breakdown with percentage shares.

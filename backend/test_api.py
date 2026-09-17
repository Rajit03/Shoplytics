"""
Shoplytics: Comprehensive FastAPI Test Suite & Performance Benchmark
Tests all API endpoints against the live running server, measures response latency,
validates payload integrity, and saves results to results/fastapi/.
"""

import os
import sys
import time
import csv
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "fastapi"))
os.makedirs(RESULTS_DIR, exist_ok=True)


TEST_ENDPOINTS = [
    ("Root", "GET", "/", 200),
    ("Health Check", "GET", "/health", 200),
    ("Dashboard Summary", "GET", "/api/dashboard/summary", 200),
    ("List Customers", "GET", "/api/customers?page=1&page_size=5", 200),
    ("Get Customer by ID", "GET", "/api/customers/0000366f3b9a7992bf8c76cfdf3221e2", 200),
    ("Top Spenders", "GET", "/api/customers/top-spenders?limit=5", 200),
    ("Search Customers", "GET", "/api/customers/search?query=00003&limit=5", 200),
    ("Customer Full Profile", "GET", "/api/customers/0000366f3b9a7992bf8c76cfdf3221e2/profile", 200),
    ("List Products", "GET", "/api/products?page=1&page_size=5", 200),
    ("Get Product by ID", "GET", "/api/products/1e9e8ef04dbcff4541ed26657ea517e5", 200),
    ("Products by Category", "GET", "/api/products/category/health_beauty?page=1&page_size=5", 200),
    ("Top Products", "GET", "/api/products/top?limit=5", 200),
    ("List Orders", "GET", "/api/orders?page=1&page_size=5", 200),
    ("Get Order by ID", "GET", "/api/orders/e481f51cbdc54678b7cc49136f2d6af7", 200),
    ("Orders by Status", "GET", "/api/orders/status/delivered?page=1&page_size=5", 200),
    ("Recent Orders", "GET", "/api/orders/recent?limit=5", 200),
    ("Customer Segments Summary", "GET", "/api/segments", 200),
    ("Cluster Profile Boundaries", "GET", "/api/segments/profiles", 200),
    ("Cluster Details", "GET", "/api/segments/2", 200),
    ("Cluster Customers", "GET", "/api/segments/2/customers?page=1&page_size=5", 200),
    ("Customer Recommendations", "GET", "/api/recommendations/0f8758e5b1c6c6b2156a9dddce128558", 200),
    ("List Recommendations", "GET", "/api/recommendations?page=1&page_size=5", 200),
    ("Association Rules", "GET", "/api/association-rules?limit=5", 200),
    ("Top Association Rules", "GET", "/api/association-rules/top?limit=5", 200),
    ("Sales Summary", "GET", "/api/sales/summary", 200),
    ("Monthly Sales", "GET", "/api/sales/monthly", 200),
    ("Category Sales", "GET", "/api/sales/categories?limit=5", 200),
    ("Product Sales", "GET", "/api/sales/products?limit=5", 200),
    ("Seller Sales", "GET", "/api/sales/sellers?limit=5", 200),
    ("Order Status Breakdown", "GET", "/api/sales/order-status", 200),
]


def run_tests():
    print("========================================")
    print("SHOPLYTICS API TEST")
    print("========================================")
    print(f"Target Server: {BASE_URL}\n")

    results = []
    passed_count = 0
    failed_count = 0

    log_lines = [
        "========================================",
        "SHOPLYTICS API TEST EXECUTION LOG",
        "========================================",
        f"Server: {BASE_URL}",
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]

    header_fmt = "{:<32} | {:<6} | {:<11} | {:<18} | {:<8}"
    row_fmt    = "{:<32} | {:<6} | {:<11} | {:<18.2f} | {:<8}"
    
    print(header_fmt.format("Endpoint Name", "Method", "HTTP Status", "Response Time (ms)", "Result"))
    print("-" * 85)

    for name, method, endpoint, expected_status in TEST_ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        try:
            t0 = time.perf_counter()
            resp = requests.request(method, url, timeout=10)
            latency_ms = (time.perf_counter() - t0) * 1000.0

            is_pass = (resp.status_code == expected_status)
            status_str = "PASSED" if is_pass else "FAILED"

            if is_pass:
                passed_count += 1
            else:
                failed_count += 1

            row_text = row_fmt.format(name, method, resp.status_code, latency_ms, status_str)
            print(row_text)
            log_lines.append(row_text)

            results.append({
                "endpoint": endpoint,
                "method": method,
                "status_code": resp.status_code,
                "response_time_ms": round(latency_ms, 2),
                "result": status_str
            })

        except Exception as e:
            failed_count += 1
            err_row = f"{name:<32} | {method:<6} | {'ERROR':<11} | {'N/A':<18} | FAILED ({e})"
            print(err_row)
            log_lines.append(err_row)
            results.append({
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time_ms": 0.0,
                "result": f"FAILED: {e}"
            })

    total_count = passed_count + failed_count
    print("-" * 85)
    summary_text = f"\nPassed: {passed_count}\nFailed: {failed_count}\nTotal:  {total_count}\n"
    print(summary_text)
    log_lines.append(summary_text)

    # Save api_performance.csv
    csv_path = os.path.join(RESULTS_DIR, "api_performance.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["endpoint", "method", "status_code", "response_time_ms", "result"])
        writer.writeheader()
        writer.writerows(results)

    # Save api_test_results.txt
    txt_path = os.path.join(RESULTS_DIR, "api_test_results.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print("========================================")
    print(f"Results saved to:")
    print(f"  - CSV: {csv_path}")
    print(f"  - TXT: {txt_path}")
    print("========================================")


if __name__ == "__main__":
    run_tests()

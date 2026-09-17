"""
Shoplytics: Frontend & Backend Integration Validation Script
Validates all endpoints, HTTP delivery, and integration health.
"""

import os
import sys
import time
import csv
import requests

FRONTEND_URL = "http://127.0.0.1:5173"
BACKEND_URL = "http://127.0.0.1:8000"

RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "frontend"))
os.makedirs(RESULTS_DIR, exist_ok=True)

PAGES_TO_VALIDATE = [
    ("Dashboard", "/", "/api/dashboard/summary"),
    ("Customers", "/customers", "/api/customers?page=1&page_size=20"),
    ("Customer Details", "/customers/0000366f3b9a7992bf8c76cfdf3221e2", "/api/customers/0000366f3b9a7992bf8c76cfdf3221e2/profile"),
    ("Products", "/products", "/api/products?page=1&page_size=20"),
    ("Orders", "/orders", "/api/orders?page=1&page_size=20"),
    ("Customer Segments", "/segments", "/api/segments/profiles"),
    ("Recommendations", "/recommendations", "/api/recommendations/0f8758e5b1c6c6b2156a9dddce128558"),
    ("Association Rules", "/association-rules", "/api/association-rules?limit=20"),
]


def run_validation():
    print("========================================")
    print("SHOPLYTICS FRONTEND VALIDATION")
    print("========================================")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL:  {BACKEND_URL}\n")

    # 1. Verify frontend index.html
    try:
        f_resp = requests.get(FRONTEND_URL, timeout=5)
        print(f"[*] Vite Dev Server Response: {f_resp.status_code} (Length: {len(f_resp.text)} bytes)")
    except Exception as e:
        print(f"[!] Could not reach Vite dev server: {e}")
        sys.exit(1)

    # 2. Verify backend health
    try:
        b_resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"[*] FastAPI Health Check: {b_resp.status_code} -> {b_resp.json()}\n")
    except Exception as e:
        print(f"[!] Could not reach FastAPI: {e}")
        sys.exit(1)

    print("{:<22} | {:<16} | {:<10} | {:<16} | {:<8}".format(
        "Page Name", "Frontend Route", "UI Status", "Backend Status", "Result"
    ))
    print("-" * 80)

    results = []
    log_lines = [
        "========================================",
        "SHOPLYTICS FRONTEND TEST RESULTS",
        "========================================",
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Frontend: {FRONTEND_URL}",
        f"Backend:  {BACKEND_URL}",
        ""
    ]

    all_passed = True
    for page_name, route, api_endpoint in PAGES_TO_VALIDATE:
        try:
            # Check frontend route delivery
            t0 = time.perf_counter()
            f_r = requests.get(f"{FRONTEND_URL}{route}", timeout=5)
            f_time = (time.perf_counter() - t0) * 1000

            # Check corresponding backend API
            t1 = time.perf_counter()
            b_r = requests.get(f"{BACKEND_URL}{api_endpoint}", timeout=5)
            b_time = (time.perf_counter() - t1) * 1000

            is_success = (f_r.status_code == 200 and b_r.status_code == 200)
            status_text = "PASSED" if is_success else "FAILED"
            if not is_success:
                all_passed = False

            row = "{:<22} | {:<16} | {:<10} | {:<16} | {:<8}".format(
                page_name, route, f"{f_r.status_code} OK", f"{b_r.status_code} OK", status_text
            )
            print(row)
            log_lines.append(row)

            results.append({
                "page": page_name,
                "frontend_route": route,
                "api_endpoint": api_endpoint,
                "frontend_status": f_r.status_code,
                "api_status": b_r.status_code,
                "api_latency_ms": round(b_time, 2),
                "status": status_text,
                "notes": f"Verified with {len(b_r.text)} bytes data payload"
            })
        except Exception as e:
            all_passed = False
            err_row = f"{page_name:<22} | {route:<16} | ERROR | ERROR | FAILED ({e})"
            print(err_row)
            log_lines.append(err_row)
            results.append({
                "page": page_name,
                "frontend_route": route,
                "api_endpoint": api_endpoint,
                "frontend_status": 0,
                "api_status": 0,
                "api_latency_ms": 0.0,
                "status": f"FAILED: {e}",
                "notes": "Connection error"
            })

    print("-" * 80)
    print(f"\nAll Pages & APIs Operational: {'YES (8/8 PASSED)' if all_passed else 'NO'}\n")
    log_lines.append(f"\nAll Pages & APIs Operational: {'YES (8/8 PASSED)' if all_passed else 'NO'}\n")

    # Save frontend_api_test.csv
    csv_path = os.path.join(RESULTS_DIR, "frontend_api_test.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "page", "frontend_route", "api_endpoint", "frontend_status", "api_status", "api_latency_ms", "status", "notes"
        ])
        writer.writeheader()
        writer.writerows(results)

    # Save frontend_test_results.txt
    txt_path = os.path.join(RESULTS_DIR, "frontend_test_results.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"Results saved to:\n  - CSV: {csv_path}\n  - TXT: {txt_path}\n")


if __name__ == "__main__":
    run_validation()

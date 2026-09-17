-- =======================================================================
-- SHOPLYTICS: PostgreSQL Demonstration & Verification Queries
-- Database: shoplytics
-- =======================================================================

-- 1. Table Row Counts
SELECT 'customers' AS table_name, COUNT(*) AS total_rows FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'analytics', COUNT(*) FROM analytics
UNION ALL
SELECT 'customer_segments', COUNT(*) FROM customer_segments
UNION ALL
SELECT 'cluster_profiles', COUNT(*) FROM cluster_profiles
UNION ALL
SELECT 'recommendations', COUNT(*) FROM recommendations
UNION ALL
SELECT 'association_rules', COUNT(*) FROM association_rules;

-- 2. Customer Lookup by Unique ID
SELECT *
FROM customers
WHERE customer_unique_id = '0000366f3b9a7992bf8c76cfdf3221e2';

-- 3. Top 10 Spending Customers
SELECT customer_unique_id, total_orders, total_spending, total_freight, average_order_value, cluster
FROM customers
ORDER BY total_spending DESC
LIMIT 10;

-- 4. Customer Distribution across K-Means Clusters
SELECT cs.cluster, cp.customers AS profile_expected_count, COUNT(cs.customer_unique_id) AS actual_count,
       ROUND(AVG(cs.total_spending), 2) AS avg_spending,
       ROUND(AVG(cs.average_order_value), 2) AS avg_aov
FROM customer_segments cs
JOIN cluster_profiles cp ON cs.cluster = cp.cluster
GROUP BY cs.cluster, cp.customers
ORDER BY cs.cluster;

-- 5. Cluster Profiles Overview
SELECT *
FROM cluster_profiles
ORDER BY cluster;

-- 6. Products by Category (e.g. 'health_beauty')
SELECT product_id, product_category_name_english, product_weight_g, product_photos_qty
FROM products
WHERE product_category_name_english = 'health_beauty'
ORDER BY product_weight_g DESC NULLS LAST
LIMIT 10;

-- 7. Recommendations for a Customer
SELECT r.customer_id, r.rank, r.product_id, p.product_category_name_english,
       r.recommendation_score, r.recommendation_source
FROM recommendations r
LEFT JOIN products p ON r.product_id = p.product_id
WHERE r.customer_id = '0f8758e5b1c6c6b2156a9dddce128558'
ORDER BY r.rank;

-- 8. Top 10 Association Rules by Lift (Apriori Output)
SELECT antecedent, consequent, support, confidence, lift
FROM association_rules
ORDER BY lift DESC
LIMIT 10;

-- 9. Total Overall Sales & Order Counts from Analytics
SELECT COUNT(DISTINCT order_id) AS total_orders,
       COUNT(*) AS total_items_sold,
       ROUND(SUM(total_item_value), 2) AS total_gross_revenue,
       ROUND(SUM(price), 2) AS total_net_product_sales,
       ROUND(SUM(freight_value), 2) AS total_freight_collected
FROM analytics;

-- 10. Monthly Sales Trend
SELECT order_year, order_month, order_month_name,
       COUNT(DISTINCT order_id) AS orders_count,
       ROUND(SUM(total_item_value), 2) AS monthly_revenue
FROM analytics
WHERE order_year IS NOT NULL
GROUP BY order_year, order_month, order_month_name
ORDER BY order_year, order_month;

-- 11. Top 10 Product Categories by Revenue
SELECT product_category_name_english,
       COUNT(*) AS total_items_sold,
       ROUND(SUM(total_item_value), 2) AS category_revenue
FROM analytics
WHERE product_category_name_english IS NOT NULL
GROUP BY product_category_name_english
ORDER BY category_revenue DESC
LIMIT 10;

-- 12. Order Status Breakdown
SELECT order_status, COUNT(*) AS count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM orders
GROUP BY order_status
ORDER BY count DESC;

-- 13. JOIN Query: High Value Customers with Cluster Segmentation & Orders
SELECT c.customer_unique_id, c.cluster, cp.min_spending, cp.max_spending,
       c.total_orders, c.total_spending, o.order_id, o.order_status, o.order_purchase_timestamp
FROM customers c
JOIN customer_segments cs ON c.customer_unique_id = cs.customer_unique_id
JOIN cluster_profiles cp ON cs.cluster = cp.cluster
JOIN orders o ON c.customer_unique_id = o.customer_id OR o.customer_id IN (
    SELECT customer_id FROM analytics a WHERE a.customer_unique_id = c.customer_unique_id LIMIT 1
)
WHERE c.cluster = 2
ORDER BY c.total_spending DESC
LIMIT 10;

-- 14. EXPLAIN ANALYZE on Customer Lookup (Index Verification)
EXPLAIN ANALYZE
SELECT * FROM customers WHERE customer_unique_id = '0000366f3b9a7992bf8c76cfdf3221e2';

-- 15. EXPLAIN ANALYZE on Recommendation Lookup (Index Verification)
EXPLAIN ANALYZE
SELECT * FROM recommendations WHERE customer_id = '0f8758e5b1c6c6b2156a9dddce128558' ORDER BY rank;

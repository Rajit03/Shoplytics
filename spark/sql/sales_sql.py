from pyspark.sql import SparkSession

# --------------------------------------------------
# CREATE SPARK SESSION
# --------------------------------------------------

spark = SparkSession.builder \
    .appName("Shoplytics-Spark-SQL") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("\n==========================================")
print("        SHOPLYTICS SPARK SQL")
print("==========================================")

# --------------------------------------------------
# READ DATA FROM HDFS
# --------------------------------------------------

input_path = (
    "hdfs://localhost:9000/"
    "shoplytics/processed/order_items_clean.csv"
)

print("\nReading data from HDFS...")
print(input_path)

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(input_path)

# --------------------------------------------------
# CREATE TEMPORARY SQL VIEW
# --------------------------------------------------

df.createOrReplaceTempView("order_items")

print("\nTemporary SQL table created: order_items")

# --------------------------------------------------
# QUERY 1: TOTAL SALES
# --------------------------------------------------

print("\n==========================================")
print("QUERY 1: TOTAL SALES")
print("==========================================")

query1 = spark.sql("""
    SELECT
        ROUND(SUM(total_item_value), 2) AS total_revenue,
        ROUND(SUM(price), 2) AS total_product_price,
        ROUND(SUM(freight_value), 2) AS total_freight
    FROM order_items
""")

query1.show()

# --------------------------------------------------
# QUERY 2: TOP 10 PRODUCTS
# --------------------------------------------------

print("\n==========================================")
print("QUERY 2: TOP 10 PRODUCTS")
print("==========================================")

query2 = spark.sql("""
    SELECT
        product_id,
        ROUND(SUM(total_item_value), 2) AS revenue,
        COUNT(*) AS items_sold
    FROM order_items
    GROUP BY product_id
    ORDER BY revenue DESC
    LIMIT 10
""")

query2.show(truncate=False)

# --------------------------------------------------
# QUERY 3: TOP 10 SELLERS
# --------------------------------------------------

print("\n==========================================")
print("QUERY 3: TOP 10 SELLERS")
print("==========================================")

query3 = spark.sql("""
    SELECT
        seller_id,
        ROUND(SUM(total_item_value), 2) AS revenue,
        COUNT(*) AS items_sold
    FROM order_items
    GROUP BY seller_id
    ORDER BY revenue DESC
    LIMIT 10
""")

query3.show(truncate=False)

# --------------------------------------------------
# QUERY 4: AVERAGE ORDER ITEM VALUE
# --------------------------------------------------

print("\n==========================================")
print("QUERY 4: AVERAGE ITEM VALUE")
print("==========================================")

query4 = spark.sql("""
    SELECT
        ROUND(AVG(total_item_value), 2) AS average_item_value
    FROM order_items
""")

query4.show()

# --------------------------------------------------
# QUERY 5: PRODUCT SALES SUMMARY
# --------------------------------------------------

print("\n==========================================")
print("QUERY 5: PRODUCT SALES SUMMARY")
print("==========================================")

query5 = spark.sql("""
    SELECT
        product_id,
        COUNT(*) AS quantity_sold,
        ROUND(SUM(price), 2) AS product_revenue,
        ROUND(SUM(freight_value), 2) AS freight_revenue,
        ROUND(SUM(total_item_value), 2) AS total_revenue
    FROM order_items
    GROUP BY product_id
    ORDER BY total_revenue DESC
""")

query5.show(10, truncate=False)

# --------------------------------------------------
# SAVE SQL RESULTS
# --------------------------------------------------

output_path = (
    "hdfs://localhost:9000/"
    "shoplytics/results/spark/sql_product_sales"
)

print("\nSaving SQL results to HDFS...")

query5.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(output_path)

# --------------------------------------------------
# COMPLETION
# --------------------------------------------------

print("\n==========================================")
print("       SPARK SQL JOB COMPLETED")
print("==========================================")

print("\nResult stored at:")
print(output_path)

spark.stop()
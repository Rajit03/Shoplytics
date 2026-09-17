from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    sum,
    count,
    avg,
    round,
    countDistinct
)

# --------------------------------------------------
# CREATE SPARK SESSION
# --------------------------------------------------

spark = SparkSession.builder \
    .appName("Shoplytics-Sales-Analytics") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("\n==========================================")
print("       SHOPLYTICS SPARK ANALYTICS")
print("==========================================")

# --------------------------------------------------
# INPUT FROM HDFS
# --------------------------------------------------

input_path = "hdfs://localhost:9000/shoplytics/processed/order_items_clean.csv"

print("\nReading data from HDFS...")
print(input_path)

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(input_path)

# --------------------------------------------------
# DATASET INFORMATION
# --------------------------------------------------

print("\n==========================================")
print("DATASET INFORMATION")
print("==========================================")

print("\nSchema:")
df.printSchema()

record_count = df.count()

print(f"\nTotal Records: {record_count}")

print("\nSample Records:")
df.show(5, truncate=False)

# --------------------------------------------------
# SALES ANALYTICS
# --------------------------------------------------

print("\n==========================================")
print("SALES ANALYTICS")
print("==========================================")

total_revenue = df.select(
    round(sum("total_item_value"), 2).alias("total_revenue")
).collect()[0]["total_revenue"]

total_price = df.select(
    round(sum("price"), 2).alias("total_price")
).collect()[0]["total_price"]

total_freight = df.select(
    round(sum("freight_value"), 2).alias("total_freight")
).collect()[0]["total_freight"]

average_item_value = df.select(
    round(avg("total_item_value"), 2).alias("average_value")
).collect()[0]["average_value"]

unique_orders = df.select(
    countDistinct("order_id").alias("unique_orders")
).collect()[0]["unique_orders"]

unique_products = df.select(
    countDistinct("product_id").alias("unique_products")
).collect()[0]["unique_products"]

unique_sellers = df.select(
    countDistinct("seller_id").alias("unique_sellers")
).collect()[0]["unique_sellers"]

print(f"\nTotal Revenue       : {total_revenue}")
print(f"Total Product Price : {total_price}")
print(f"Total Freight       : {total_freight}")
print(f"Average Item Value  : {average_item_value}")
print(f"Unique Orders       : {unique_orders}")
print(f"Unique Products     : {unique_products}")
print(f"Unique Sellers      : {unique_sellers}")

# --------------------------------------------------
# TOP 10 PRODUCTS
# --------------------------------------------------

print("\n==========================================")
print("TOP 10 PRODUCTS BY REVENUE")
print("==========================================")

product_sales = df.groupBy("product_id") \
    .agg(
        round(sum("total_item_value"), 2).alias("revenue"),
        count("*").alias("items_sold")
    ) \
    .orderBy("revenue", ascending=False)

product_sales.show(10, truncate=False)

# --------------------------------------------------
# TOP 10 SELLERS
# --------------------------------------------------

print("\n==========================================")
print("TOP 10 SELLERS BY REVENUE")
print("==========================================")

seller_sales = df.groupBy("seller_id") \
    .agg(
        round(sum("total_item_value"), 2).alias("revenue"),
        count("*").alias("items_sold")
    ) \
    .orderBy("revenue", ascending=False)

seller_sales.show(10, truncate=False)

# --------------------------------------------------
# SAVE PRODUCT RESULTS TO HDFS
# --------------------------------------------------

product_output = (
    "hdfs://localhost:9000/"
    "shoplytics/results/spark/product_sales"
)

print("\nSaving product analytics to HDFS...")

product_sales.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(product_output)

# --------------------------------------------------
# SAVE SELLER RESULTS TO HDFS
# --------------------------------------------------

seller_output = (
    "hdfs://localhost:9000/"
    "shoplytics/results/spark/seller_sales"
)

print("Saving seller analytics to HDFS...")

seller_sales.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(seller_output)

# --------------------------------------------------
# COMPLETION
# --------------------------------------------------

print("\n==========================================")
print("       SPARK JOB COMPLETED SUCCESSFULLY")
print("==========================================")

print("\nResults stored in HDFS:")
print(product_output)
print(seller_output)

spark.stop()
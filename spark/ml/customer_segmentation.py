from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.sql.functions import (
    avg,
    min,
    max,
    count
)

# ==================================================
# CREATE SPARK SESSION
# ==================================================

spark = SparkSession.builder \
    .appName("Shoplytics-Customer-Segmentation") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("\n==========================================")
print("   SHOPLYTICS CUSTOMER SEGMENTATION")
print("==========================================")

# ==================================================
# READ CUSTOMER FEATURES FROM HDFS
# ==================================================

input_path = (
    "hdfs://localhost:9000/"
    "shoplytics/processed/customer_features.csv"
)

print("\nReading customer features from HDFS...")
print(input_path)

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(input_path)

print("\n==========================================")
print("CUSTOMER DATA")
print("==========================================")

df.printSchema()

print("\nTotal Customers:", df.count())

print("\nSample Customers:")
df.show(5, truncate=False)

# ==================================================
# SELECT FEATURES
# ==================================================

feature_columns = [
    "total_orders",
    "total_spending",
    "total_freight",
    "total_products",
    "average_order_value"
]

print("\nFeatures used for K-Means:")
for feature in feature_columns:
    print("-", feature)

# ==================================================
# HANDLE NULL VALUES
# ==================================================

df = df.dropna(subset=feature_columns)

# ==================================================
# CREATE FEATURE VECTOR
# ==================================================

assembler = VectorAssembler(
    inputCols=feature_columns,
    outputCol="raw_features"
)

assembled_df = assembler.transform(df)

# ==================================================
# STANDARDIZE FEATURES
# ==================================================

scaler = StandardScaler(
    inputCol="raw_features",
    outputCol="features",
    withStd=True,
    withMean=True
)

scaler_model = scaler.fit(assembled_df)

scaled_df = scaler_model.transform(assembled_df)

print("\nFeature vector created and standardized.")

# ==================================================
# K-MEANS CLUSTERING
# ==================================================

print("\n==========================================")
print("K-MEANS CLUSTERING")
print("==========================================")

k = 4

print(f"\nNumber of clusters (K): {k}")

kmeans = KMeans(
    k=k,
    seed=42,
    featuresCol="features",
    predictionCol="cluster"
)

model = kmeans.fit(scaled_df)

predictions = model.transform(scaled_df)

# ==================================================
# CLUSTER CENTERS
# ==================================================

print("\nCluster Centers:")

centers = model.clusterCenters()

for i, center in enumerate(centers):
    print(f"\nCluster {i}:")
    print(center)

# ==================================================
# CUSTOMER CLUSTER COUNTS
# ==================================================

print("\n==========================================")
print("CUSTOMERS PER CLUSTER")
print("==========================================")

cluster_counts = predictions.groupBy("cluster") \
    .count() \
    .orderBy("cluster")

cluster_counts.show()

# ==================================================
# CLUSTER PROFILE
# ==================================================

print("\n==========================================")
print("CUSTOMER CLUSTER PROFILES")
print("==========================================")

cluster_profile = predictions.groupBy("cluster").agg(
    count("*").alias("customers"),
    avg("total_orders").alias("avg_orders"),
    avg("total_spending").alias("avg_spending"),
    avg("total_freight").alias("avg_freight"),
    avg("total_products").alias("avg_products"),
    avg("average_order_value").alias("avg_order_value"),
    min("total_spending").alias("min_spending"),
    max("total_spending").alias("max_spending")
).orderBy("cluster")

cluster_profile.show(truncate=False)

# ==================================================
# SAVE CUSTOMER SEGMENTS
# ==================================================

output_path = (
    "hdfs://localhost:9000/"
    "shoplytics/results/spark/customer_segments"
)

print("\nSaving customer segments to HDFS...")

result_df = predictions.select(
    "customer_unique_id",
    "total_orders",
    "total_spending",
    "total_freight",
    "total_products",
    "average_order_value",
    "cluster"
)

result_df.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(output_path)

# ==================================================
# SAVE CLUSTER PROFILES
# ==================================================

profile_output = (
    "hdfs://localhost:9000/"
    "shoplytics/results/spark/cluster_profiles"
)

print("Saving cluster profiles to HDFS...")

cluster_profile.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(profile_output)

# ==================================================
# FINAL MESSAGE
# ==================================================

print("\n==========================================")
print(" CUSTOMER SEGMENTATION COMPLETED")
print("==========================================")

print("\nCustomer segments:")
print(output_path)

print("\nCluster profiles:")
print(profile_output)

spark.stop()
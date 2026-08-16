import os
from pyspark.sql.functions import col

from session import get_spark, get_jdbc_url

spark = get_spark("CleanOrders")

# Read from S3 (bucket/prefix via env var, defaults to the olist raw data location)
data_path = os.environ.get("DATA_PATH", "s3a://olist-raw-daud/raw")
df = spark.read.option("header", True).option("inferSchema", True).csv(f"{data_path}/olist_orders_dataset.csv")

# Transformations
df_clean = (df
            .withColumn("order_purchase_timestamp", col("order_purchase_timestamp").cast("timestamp"))
            .withColumn("order_approved_at", col("order_approved_at").cast("timestamp"))
            .withColumn("order_delivered_carrier_date", col("order_delivered_carrier_date").cast("timestamp"))
            .withColumn("order_delivered_customer_date", col("order_delivered_customer_date").cast("timestamp"))
            .withColumn("order_estimated_delivery_date", col("order_estimated_delivery_date").cast("timestamp"))
            )

df_deduped = df_clean.drop_duplicates(["order_id"])

# Database configurations - RDS in production, local Docker Postgres by default
db_user = os.environ.get("OLIST_DB_USER", "olist_user")
db_password = os.environ.get("OLIST_DB_PASSWORD", "olist_password")
jdbc_url = get_jdbc_url()

# Write out to the warehouse target
df_deduped.write.option("truncate", "true").jdbc(
    url=jdbc_url,
    table="orders",
    mode="overwrite",
    properties={'user': db_user, 'password': db_password, 'driver': 'org.postgresql.Driver'}
)

# Sanity check count printout for Airflow task logs
count = df_deduped.count()
print(f"Successfully processed and loaded {count} rows into table: orders")

spark.stop()

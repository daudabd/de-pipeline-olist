import os
from pyspark.sql.functions import col

from session import get_spark, get_jdbc_url

spark = get_spark("OrderItems")

# Read from S3 (bucket/prefix via env var, defaults to the olist raw data location)
data_path = os.environ.get("DATA_PATH", "s3a://olist-raw-daud/raw")
df = spark.read.option("header", True).option("inferSchema", True).csv(f"{data_path}/olist_order_items_dataset.csv")

# Transformations
df_clean = (df
            .withColumn("shipping_limit_date", col("shipping_limit_date").cast("timestamp"))
            )

df_deduped = df_clean.drop_duplicates(["order_id", "order_item_id"])

# Database configurations - RDS in production, local Docker Postgres by default
db_user = os.environ.get("OLIST_DB_USER", "olist_user")
db_password = os.environ.get("OLIST_DB_PASSWORD", "olist_password")
jdbc_url = get_jdbc_url()

# Write out to the warehouse target
df_deduped.write.option("truncate", "true").jdbc(
    url=jdbc_url,
    table="order_items",
    mode="overwrite",
    properties={'user': db_user, 'password': db_password, 'driver': 'org.postgresql.Driver'}
)

# Verification read to log processing outputs
df_verified = spark.read.jdbc(
    url=jdbc_url,
    table="order_items",
    properties={'user': db_user, 'password': db_password, 'driver': 'org.postgresql.Driver'}
)

print(f"Successfully processed and loaded {df_verified.count()} rows into table: order_items")

spark.stop()

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark using the internal container path for the JDBC jar
spark = (SparkSession.builder
        .appName("OrderItems")
        .config("spark.jars", "/opt/airflow/jdbc_driver/postgresql-42.7.11.jar")
        .getOrCreate()
)

# Read from the container's mounted data folder
df = spark.read.option("header", True).option("inferSchema", True).csv("/opt/airflow/data/raw/olist_order_items_dataset.csv")

# Transformations
df_clean = (df
            .withColumn("shipping_limit_date", col("shipping_limit_date").cast("timestamp"))
            )

df_deduped = df_clean.drop_duplicates(["order_id", "order_item_id"])

# Database configurations pointing to the internal Docker service network
db_user = os.environ.get("OLIST_DB_USER", "olist_user")
db_password = os.environ.get("OLIST_DB_PASSWORD", "olist_password")
jdbc_url = "jdbc:postgresql://olist-postgres:5432/olist_db"

# Write out to the warehouse target
df_deduped.write.jdbc(
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
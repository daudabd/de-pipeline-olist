import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark using the internal container path for the JDBC jar
spark = (SparkSession.builder
         .appName("CleanOrders")
         .config("spark.jars", "/opt/airflow/jdbc_driver/postgresql-42.7.11.jar")
         .getOrCreate()
)

# Read from the container's mounted data folder
df = spark.read.option("header", True).option("inferSchema", True).csv("/opt/airflow/data/raw/olist_orders_dataset.csv")

# Transformations
df_clean = (df
            .withColumn("order_purchase_timestamp", col("order_purchase_timestamp").cast("timestamp"))
            .withColumn("order_approved_at", col("order_approved_at").cast("timestamp"))
            .withColumn("order_delivered_carrier_date", col("order_delivered_carrier_date").cast("timestamp"))
            .withColumn("order_delivered_customer_date", col("order_delivered_customer_date").cast("timestamp"))
            .withColumn("order_estimated_delivery_date", col("order_estimated_delivery_date").cast("timestamp"))
            )

df_deduped = df_clean.drop_duplicates(["order_id"])

# Database configurations pointing to the internal Docker service network
db_user = os.environ.get("OLIST_DB_USER", "olist_user")
db_password = os.environ.get("OLIST_DB_PASSWORD", "olist_password")
jdbc_url = "jdbc:postgresql://olist-postgres:5432/olist_db"

# Write out to the warehouse target
df_deduped.write.jdbc(
    url=jdbc_url,
    table="orders",
    mode="overwrite",
    properties={'user': db_user, 'password': db_password, 'driver': 'org.postgresql.Driver'}
)

# Sanity check count printout for Airflow task logs
count = df_deduped.count()
print(f"Successfully processed and loaded {count} rows into table: orders")

spark.stop()
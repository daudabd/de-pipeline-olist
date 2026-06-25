from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os


spark = ( SparkSession.builder
         .appName("CleanOrders")
         .config("spark.jars", "/Users/daud/Desktop/jdbc_driver/postgresql-42.7.11.jar")
         .getOrCreate()
)

df = spark.read.option("header", True).option("inferSchema", True).csv("data/raw/olist_orders_dataset.csv")

df_clean = (df
            .withColumn("order_purchase_timestamp", col("order_purchase_timestamp").cast("timestamp"))
            .withColumn("order_approved_at", col("order_approved_at").cast("timestamp"))
            .withColumn("order_delivered_carrier_date", col("order_delivered_carrier_date").cast("timestamp"))
            .withColumn("order_delivered_customer_date", col("order_delivered_customer_date").cast("timestamp"))
            .withColumn("order_estimated_delivery_date", col("order_estimated_delivery_date").cast("timestamp"))
            )

df_deduped = df_clean.drop_duplicates(["order_id"])

df_deduped.write.jdbc(
    url= "jdbc:postgresql://localhost:5433/olist_db",
    table= "orders",
    mode= "overwrite",
    properties= {'user': os.environ.get("OLIST_DB_USER"), 'password': os.environ.get("OLIST_DB_PASSWORD"), 'driver': 'org.postgresql.Driver'}
)

spark.read.jdbc(
    url= "jdbc:postgresql://localhost:5433/olist_db",
    table= "orders",
    properties= {'user': os.environ.get("OLIST_DB_USER"), 'password': os.environ.get("OLIST_DB_PASSWORD"), 'driver': 'org.postgresql.Driver'}
)

count = df_deduped.count()
print(count)


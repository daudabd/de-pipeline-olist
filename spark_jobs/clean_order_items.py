from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os


spark = (SparkSession.builder
        .appName("OrderItems")
        .config("spark.jars", "/Users/daud/Desktop/jdbc_driver/postgresql-42.7.11.jar")
        .getOrCreate()
)

df = spark.read.option("header", True).option("inferSchema", True).csv("data/raw/olist_order_items_dataset.csv")

df_clean = (df
            .withColumn("shipping_limit_date", col("shipping_limit_date").cast("timestamp"))
            )

df_deduped = df_clean.drop_duplicates(["order_id", "order_item_id"])

df_deduped.write.jdbc(
    url= "jdbc:postgresql://localhost:5433/olist_db",
    table= "order_items",
    mode= "overwrite",
    properties= {'user': os.environ.get("OLIST_DB_USER"), 'password': os.environ.get("OLIST_DB_PASSWORD"), 'driver': 'org.postgresql.Driver'}
)

df_verified = spark.read.jdbc(
    url="jdbc:postgresql://localhost:5433/olist_db",
    table="order_items",
    properties={'user': os.environ.get("OLIST_DB_USER"), 'password': os.environ.get("OLIST_DB_PASSWORD"), 'driver': 'org.postgresql.Driver'}
)

print(f"Rows in order_items: {df_verified.count()}")






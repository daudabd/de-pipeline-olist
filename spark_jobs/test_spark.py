from pyspark.sql import SparkSession

spark = (SparkSession.builder
         .appName("OlistTest")
        .getOrCreate()
)

df = spark.read.option("header", True).option("inferSchema", True).csv("data/raw/olist_orders_dataset.csv")

df.printSchema()
df.show(5)
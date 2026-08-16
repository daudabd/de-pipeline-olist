import os
import sys

from session import get_spark, get_jdbc_url

EXPECTED_COUNTS = {
    "orders": 99441,
    "order_items": 112650,
}

spark = get_spark("ValidatePipeline")

# Database configurations - RDS in production, local Docker Postgres by default
db_user = os.environ.get("OLIST_DB_USER", "olist_user")
db_password = os.environ.get("OLIST_DB_PASSWORD", "olist_password")
jdbc_url = get_jdbc_url()


def table_count(table):
    df = (spark.read.format("jdbc")
          .option("url", jdbc_url)
          .option("query", f"SELECT COUNT(*) AS cnt FROM {table}")
          .option("user", db_user)
          .option("password", db_password)
          .option("driver", "org.postgresql.Driver")
          .load())
    return df.collect()[0]["cnt"]


all_passed = True
for table, expected in EXPECTED_COUNTS.items():
    actual = table_count(table)
    if actual == expected:
        print(f"PASS: {table} count is {actual} (expected {expected})")
    else:
        print(f"FAIL: {table} count is {actual} (expected {expected})")
        all_passed = False

spark.stop()

if not all_passed:
    sys.exit(1)

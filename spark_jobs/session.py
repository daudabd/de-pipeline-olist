import os
from pyspark.sql import SparkSession

JAR_DIR = os.environ.get("JAR_DIR", os.path.expanduser("~/jdbc_drivers"))

JDBC_JAR = os.path.join(JAR_DIR, "postgresql-42.7.11.jar")
HADOOP_AWS_JAR = os.path.join(JAR_DIR, "hadoop-aws-3.5.0.jar")
AWS_SDK_JAR = os.path.join(JAR_DIR, "bundle-2.35.4.jar")
AAL_JAR = os.path.join(JAR_DIR, "analyticsaccelerator-s3-1.3.1.jar")


def get_spark(app_name):
    return (SparkSession.builder
            .appName(app_name)
            .config("spark.jars", ",".join([JDBC_JAR, HADOOP_AWS_JAR, AWS_SDK_JAR, AAL_JAR]))
            .config("spark.hadoop.fs.s3a.access.key", os.environ.get("AWS_ACCESS_KEY_ID", ""))
            .config("spark.hadoop.fs.s3a.secret.key", os.environ.get("AWS_SECRET_ACCESS_KEY", ""))
            .config("spark.hadoop.fs.s3a.endpoint", "s3.us-west-2.amazonaws.com")
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .config("spark.hadoop.fs.s3a.input.stream.type", "classic")
            .config("spark.hadoop.fs.s3a.connection.timeout", 200000)
            .config("spark.hadoop.fs.s3a.connection.establish.timeout", 60000)
            .config("spark.hadoop.fs.s3a.socket.timeout", 60000)
            .config("spark.hadoop.fs.s3a.threads.keepalivetime", 60)
            .config("spark.hadoop.fs.s3a.aws.credentials.provider",
                    "org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider,"
                    "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider,"
                    "org.apache.hadoop.fs.s3a.auth.IAMInstanceCredentialsProvider")
            .getOrCreate())


def get_jdbc_url():
    rds_endpoint = os.environ.get("RDS_ENDPOINT")
    if rds_endpoint:
        return f"jdbc:postgresql://{rds_endpoint}:5432/olist_db"
    return "jdbc:postgresql://localhost:5433/olist_db"

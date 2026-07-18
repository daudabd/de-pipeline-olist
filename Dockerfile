FROM apache/airflow:3.2.2-python3.11

USER root

# Install OpenJDK 17 and postgresql-client for verification checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jdk postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Java environment variables required by PySpark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow

# Install PySpark matching your local configuration
RUN pip install --no-cache-dir pyspark==4.1.2
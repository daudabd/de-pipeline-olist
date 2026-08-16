FROM apache/airflow:3.2.2

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jdk postgresql-client curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow

RUN pip install pyspark
RUN pip install dbt-core dbt-postgres

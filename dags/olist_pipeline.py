from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

# Default arguments setting retries and ownership
default_args = {
    'owner': 'daud',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='olist_pipeline',
    default_args=default_args,
    description='Olist Data Pipeline - PySpark Batch Transformations',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    clean_orders_task = BashOperator(
        task_id='clean_orders_task',
        bash_command='python /opt/airflow/spark_jobs/clean_orders.py'
    )

    clean_order_items_task = BashOperator(
        task_id='clean_order_items_task',
        bash_command='python /opt/airflow/spark_jobs/clean_order_items.py'
    )

    verify_counts_task = BashOperator(
        task_id='verify_counts_task',
        bash_command='python /opt/airflow/spark_jobs/validate_pipeline.py'
    )

    dbt_run_task = BashOperator(
        task_id='dbt_run_task',
        bash_command='cd /opt/airflow/olist_dbt && dbt run'
    )

    dbt_test_task = BashOperator(
        task_id='dbt_test_task',
        bash_command='cd /opt/airflow/olist_dbt && dbt test'
    )

    # Parallel cleaning tasks execution pattern flowing into validation target
    [clean_orders_task, clean_order_items_task] >> verify_counts_task >> dbt_run_task >> dbt_test_task
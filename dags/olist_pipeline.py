from datetime import datetime, timedelta
from airflow import DAG
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
) as dag:

    clean_orders_task = BashOperator(
        task_id='clean_orders_task',
        bash_command='python /opt/airflow/spark_jobs/clean_orders.py'
    )

    clean_order_items_task = BashOperator(
        task_id='clean_order_items_task',
        bash_command='python /opt/airflow/spark_jobs/clean_order_items.py'
    )

    # Uses internal Docker networking DNS (olist-postgres) to query row assertions
    verify_counts_task = BashOperator(
        task_id='verify_counts_task',
        bash_command=(
            'PGPASSWORD=olist_password psql -h olist-postgres -U olist_user -d olist_db -c '
            '"SELECT \'orders\' as table_name, COUNT(*) FROM orders UNION ALL '
            'SELECT \'order_items\', COUNT(*) FROM order_items;"'
        )
    )

    # Parallel cleaning tasks execution pattern flowing into validation target
    [clean_orders_task, clean_order_items_task] >> verify_counts_task
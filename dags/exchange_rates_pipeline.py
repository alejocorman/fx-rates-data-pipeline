from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "milka",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="exchange_rates_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@once",
    catchup=False,
    default_args=default_args,
    tags=["exchange_rates", "dbt"],
) as dag:

    extract = BashOperator(
        task_id="extract_frankfurter",
        bash_command="python /opt/airflow/src/ingest_api.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test",
    )

    extract >> dbt_run >> dbt_test

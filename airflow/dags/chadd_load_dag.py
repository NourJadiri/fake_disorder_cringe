import airflow
import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from src.utils.mongo import create_production_db
from src.reddit_scrapping import connect_to_mongo, test_mongo


default_args_dict = {
    'start_date': airflow.utils.dates.days_ago(0),
    'concurrency': 1,
    'retries': 0,
    'retry_delay': datetime.timedelta(minutes=5),
}

chadd_dag = DAG(
    dag_id='chadd_load_dag',
    default_args=default_args_dict,
    catchup=False,
)

#----------------------

def branch_on_mango_connection():
    if connect_to_mongo():
        return 'clean_ingestion_db'
    else:
        return 'stop_task'

# Task to check MongoDB connection
check_mongo_task = PythonOperator(
    task_id='check_mongo_task',
    dag=chadd_dag,
    python_callable=test_mongo,
)

create_production_db_task = PythonOperator(
    task_id='create_production_db',
    dag=chadd_dag,
    python_callable=create_production_db,
)






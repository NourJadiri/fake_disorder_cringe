import airflow
import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator

from src.chadd_prod_loading import *
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

clean_prod_db_task = PythonOperator(
    task_id='clean_ingestion_db',
    dag=chadd_dag,
    python_callable=clean_prod_db,
)

create_production_db_task = PythonOperator(
    task_id='create_production_db',
    dag=chadd_dag,
    python_callable=create_production_db,
)

def branch_on_staging_db_check():
    if check_staging_db():
        return 'create_production_db'
    else:
        return 'stop_task'

# Branch task based on staging database check
branch_staging_db_task = BranchPythonOperator(
    task_id='branch_staging_db_task',
    dag=chadd_dag,
    python_callable=branch_on_staging_db_check,
)

load_posts_to_prod_db_task = PythonOperator(
    task_id='load_posts_to_prod_db',
    dag=chadd_dag,
    python_callable=load_posts_to_prod_db,
)

load_members_to_prod_db_task = PythonOperator(
    task_id='load_members_to_prod_db',
    dag=chadd_dag,
    python_callable=load_members_to_prod_db,
)

stop_task = PythonOperator(
    task_id='stop_task',
    dag=chadd_dag,
    python_callable=lambda: print("Stopping the DAG."),
)

check_mongo_task >> clean_prod_db_task >> branch_staging_db_task >> [create_production_db_task, stop_task]
create_production_db_task >> load_members_to_prod_db_task >> load_posts_to_prod_db_task




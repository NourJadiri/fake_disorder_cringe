import airflow
import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from src.reddit_scrapping import test_mongo
from src.augmenting_data import augment_documents,test_mongo
import os
from datetime import datetime, timedelta  # Import timedelta here

# Assuming you want the DAG to start on Dec 18, 2024, at 10 AM UTC
start_date = datetime(2024, 12, 18, 10, 0)  # Adjust this to the current day if needed
end_date = datetime(2024, 12, 28, 10, 0)  # 10 days after


# Define default arguments
default_args_dict = {
    'start_date': airflow.utils.dates.days_ago(0),
    'concurrency': 1,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
augment_data_dag = DAG(
    dag_id='augment_data_dag',
    description='A DAG to augment data',
    default_args=default_args_dict,
    schedule_interval='0 0-23/2 * * *',  # Runs every 2 hours (approximately 10 times/day)
    catchup=False,  # Backfill any missed runs
    max_active_runs=1,  # Ensure only one task is active at a time
)

#----------------------
#Start of functions
#----------------------

def augmentData():
    return augment_documents(100)

#----------------------
#End of functions
#----------------------

#----------------------
#Start of tasks
#----------------------






task_zero = PythonOperator(
    task_id='test_mongo_connection',
    dag=augment_data_dag,
    python_callable=test_mongo,
    trigger_rule='all_success', 
    depends_on_past=False,
)

task_one = PythonOperator(
    task_id='augment_data',
    dag=augment_data_dag,
    python_callable=augmentData,
    trigger_rule='all_success', 
    depends_on_past=False,
)









#----------------------
#End of tasks
#----------------------

#----------------------
#Task Dependencies
#----------------------

task_zero >> task_one


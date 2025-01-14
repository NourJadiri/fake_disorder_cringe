import airflow
import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from src.augmenting_data import augment_documents,clean_data
from src.reddit_scrapping import  get_reddit_posts

import os
from datetime import datetime, timedelta  # Import timedelta here



# Define default arguments
default_args_dict = {
    'start_date': airflow.utils.dates.days_ago(0),
    'concurrency': 1,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
reddit_dag = DAG(
    dag_id='reddit_dag',
    description='A DAG to augment data',
    default_args=default_args_dict,
    schedule_interval='@weekly',  # Runs once a week
    catchup=False,  # Backfill any missed runs
    max_active_runs=1,  # Ensure only one task is active at a time
)

#----------------------
#Start of functions
#----------------------

def augmentData():
    return augment_documents(100)
def Clean():
    return clean_data(100)

#----------------------
#End of functions
#----------------------

#----------------------
#Start of tasks
#----------------------




task_zero = PythonOperator(
    task_id='Scrap_reddit_posts',
    dag=reddit_dag,
    python_callable=get_reddit_posts,
    trigger_rule='all_success', 
    depends_on_past=False,
)




task_one = PythonOperator(
    task_id='augment_data_with_llm',
    dag=reddit_dag,
    python_callable=augmentData,
    trigger_rule='all_success', 
    depends_on_past=False,
)

task_two = PythonOperator(
    task_id='clean_data',
    dag=reddit_dag,
    python_callable=Clean,
    trigger_rule='all_success', 
    depends_on_past=False,
)







#----------------------
#End of tasks
#----------------------


task_zero >> task_one >> task_two


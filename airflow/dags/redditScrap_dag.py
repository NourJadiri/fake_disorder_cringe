import airflow
import datetime
import pandas as pd
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from src.reddit_scrapping import connect_to_mongo, connect_to_redis, connect_to_reddit, get_reddit_posts,test_connections,test_redis,test_mongo
import os


default_args_dict = {
    'start_date': airflow.utils.dates.days_ago(0),
    'concurrency': 1,
    'schedule_interval': '0 0 * * 0-4',
    'retries': 0,
    'retry_delay': datetime.timedelta(minutes=5),
}

redditScrap_dag = DAG(
    dag_id='redditScrap_dag',
    default_args=default_args_dict,
    catchup=False,
)

#----------------------
#Start of functions
#----------------------

#----------------------
#End of functions
#----------------------

#----------------------
#Start of tasks
#----------------------






task_one = PythonOperator(
    task_id='scrap_reddit',
    dag=redditScrap_dag,
    python_callable=test_redis,
    trigger_rule='all_success', 
    depends_on_past=False,
)

task_zero = PythonOperator(
    task_id='test_connections',
    dag=redditScrap_dag,
    python_callable=test_mongo,
    trigger_rule='all_success', 
    depends_on_past=False,
)

task_two = PythonOperator(
    task_id='test_connection_to_mongo',
    dag=redditScrap_dag,
    python_callable=get_reddit_posts,
    trigger_rule='all_success', 
    depends_on_past=False,
)








#----------------------
#End of tasks
#----------------------

#----------------------
#Task Dependencies
#----------------------

task_one >> task_zero >> task_two


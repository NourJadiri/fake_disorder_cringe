import airflow
import datetime
import pandas as pd
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator

from src.chadd_scraping import check_cookie_file
from src.reddit_scrapping import connect_to_mongo, connect_to_redis, connect_to_reddit, get_reddit_posts,test_connections,test_redis,test_mongo
import os


default_args_dict = {
    'start_date': airflow.utils.dates.days_ago(0),
    'concurrency': 1,
    'retries': 0,
    'retry_delay': datetime.timedelta(minutes=5),
}

chadd_dag = DAG(
    dag_id='chadd_dag',
    default_args=default_args_dict,
    catchup=False,
)

#----------------------

check_cookie_task = PythonOperator(
    task_id='check_cookie',
    dag=chadd_dag,
    python_callable=check_cookie_file,
    trigger_rule='all_success',
    depends_on_past=False,
)

# check if cookie file is available
# if yes, start scraping
# if no, login and save cookies

# We can pass the cookies as xcom variables
# We can also pass the cookies as environment variables

# test mongo connection

# fetch post ids, store them in a file

# fetch post details, store them in a collection

# go fetch all the members of the community

# fetch user details, store them in a collection

# enjoy the data



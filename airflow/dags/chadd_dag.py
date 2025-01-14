import airflow
import datetime
import pandas as pd
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator

from src.chadd_scraping import *
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

def branch_on_check_cookies(**kwargs):
    # Assuming check_cookie_file returns a boolean
    if kwargs['ti'].xcom_pull(task_ids='check_cookie'):
        return 'load_scraper_from_cookies'
    else:
        return 'init_scraper_task'

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

clean_ingestion_db_task = PythonOperator(
    task_id='clean_ingestion_db',
    dag=chadd_dag,
    python_callable=clean_ingestion_db_func,
)

clean_staging_db_task = PythonOperator(
    task_id='clean_staging_db',
    dag=chadd_dag,
    python_callable=clean_staging_db_func,
)

# Branch task based on MongoDB connection
branch_mongo_task = BranchPythonOperator(
    task_id='branch_mongo_task',
    dag=chadd_dag,
    python_callable=branch_on_mango_connection,
    provide_context=True,
)

check_cookie_task = PythonOperator(
    task_id='check_cookie',
    dag=chadd_dag,
    python_callable=check_cookie_file,
    trigger_rule='all_success',
    depends_on_past=False,
)

found_cookies = BranchPythonOperator(
    task_id='found_cookies',
    dag=chadd_dag,
    python_callable=branch_on_check_cookies,
    provide_context=True,
)

load_scraper_from_cookies = PythonOperator(
    task_id='load_scraper_from_cookies',
    dag=chadd_dag,
    python_callable=load_scraper_from_cookies,
)

init_scraper_task = PythonOperator(
    task_id='init_scraper_task',
    dag=chadd_dag,
    python_callable=init_chadd_scraper,  # Define this function
)

# Stop task if MongoDB connection fails
stop_task = DummyOperator(
    task_id='stop_task',
    dag=chadd_dag,
)

fetch_posts_task = PythonOperator(
    task_id='fetch_posts_task',
    dag=chadd_dag,
    python_callable=fetch_posts_task,
    trigger_rule='none_failed_min_one_success',
)

fetch_members_task = PythonOperator(
    task_id='fetch_members_task',
    dag=chadd_dag,
    python_callable=fetch_members,
)

fill_posts_collection_task = PythonOperator(
    task_id='fill_posts_collection_task',
    dag=chadd_dag,
    python_callable=fetch_post_details,
)


fill_members_collection_task = PythonOperator(
    task_id='fill_members_collection_task',
    dag=chadd_dag,
    python_callable=fetch_members_details,
)

infer_gender_task = PythonOperator(
    task_id='infer_gender_task',
    dag=chadd_dag,
    python_callable=infer_gender_from_bio,
)

homogenize_gender_task = PythonOperator(
    task_id = 'homogenize_gender_task',
    dag = chadd_dag,
    python_callable = homogenize_gender,
)

analyze_sentiment_task = PythonOperator(
    task_id = 'analyze_sentiment_task',
    dag = chadd_dag,
    python_callable = analyze_sentiment,
)

classify_self_diagnosis_and_medication_task = PythonOperator(
    task_id = 'classify_self_diagnosis_and_medication_task',
    dag = chadd_dag,
    python_callable = classify_self_diagnosis_and_medication,
)

# noinspection PyStatementEffect
check_mongo_task >> branch_mongo_task >> [clean_ingestion_db_task, stop_task]
# noinspection PyStatementEffect
clean_ingestion_db_task >> clean_staging_db_task >> check_cookie_task >> found_cookies >> [load_scraper_from_cookies, init_scraper_task] >> fetch_posts_task >> fetch_members_task
# noinspection PyStatementEffect
fetch_members_task >> fill_posts_collection_task >> fill_members_collection_task >> infer_gender_task >> homogenize_gender_task >> analyze_sentiment_task >> classify_self_diagnosis_and_medication_task



# fields to keep : Mention of Solutions, Personal_Experience, Self-Diagnosis, Self-Medication, Sentiment, Topic
# enjoy the data



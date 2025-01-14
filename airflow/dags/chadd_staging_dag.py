import airflow
import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator

from src.reddit_scrapping import test_mongo
from src.utils.mongo import connect_to_mongo
from src.chadd_scraping import *



default_args_dict = {
    'start_date': airflow.utils.dates.days_ago(0),
    'concurrency': 1,
    'retries': 0,
    'retry_delay': datetime.timedelta(minutes=5),
}

chadd_dag = DAG(
    dag_id='chadd_staging_dag',
    default_args=default_args_dict,
    catchup=False,
)

check_mongo_task = PythonOperator(
    task_id='check_mongo_task',
    dag=chadd_dag,
    python_callable=test_mongo,
)

def branch_on_mango_connection():
    if connect_to_mongo():
        return 'clean_staging_db'
    else:
        return 'stop_task'

branch_mongo_task = BranchPythonOperator(
    task_id='branch_mongo_task',
    dag=chadd_dag,
    python_callable=branch_on_mango_connection,
)

clean_staging_db_task = PythonOperator(
    task_id='clean_staging_db',
    dag=chadd_dag,
    python_callable=clean_staging_db_func,
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

stop_task = DummyOperator(
    task_id='stop_task',
    dag=chadd_dag,
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




# check mongo connection
# infer gender
# homogenize gender
# analyze sentiment
# classify self diagnosis and medication

check_mongo_task >> branch_mongo_task >> [clean_staging_db_task, stop_task]
clean_staging_db_task >> fill_posts_collection_task >> fill_members_collection_task >>infer_gender_task >> homogenize_gender_task >> analyze_sentiment_task >> classify_self_diagnosis_and_medication_task
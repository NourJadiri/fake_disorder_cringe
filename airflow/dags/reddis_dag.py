from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import redis

def redis_example_task():
    # Connection details for Redis
    redis_host = 'redis'  # Docker service name for Redis
    redis_port = 6379
    redis_db = 0

    try:
        # Establish a connection to Redis
        client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

        # Perform basic operations
        client.set('airflow_key', 'Hello, Redis from Airflow!')
        value = client.get('airflow_key')

        print(f"Retrieved value from Redis: {value.decode('utf-8')}")

    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        raise

# Define the DAG
with DAG(
    dag_id='redis_connection_dag',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # Create a PythonOperator
    redis_task = PythonOperator(
        task_id='test_redis_connection',
        python_callable=redis_example_task
    )

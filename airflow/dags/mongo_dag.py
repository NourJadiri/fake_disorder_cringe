from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import os

def mongo_example_task():
    # MongoDB connection details
    mongo_host = 'mongo'  # Docker service name for MongoDB
    mongo_port = 27017
    database_name = 'airflow_db'
    collection_name = 'example_collection'

    try:
        # Establish connection to MongoDB
        client = MongoClient(host=mongo_host, port=mongo_port)

        # Access database and collection
        db = client[database_name]
        collection = db[collection_name]

        # Insert a document
        document = {"message": "Hello, MongoDB from Airflow!", "timestamp": datetime.now()}
        insert_result = collection.insert_one(document)
        print(f"Inserted document ID: {insert_result.inserted_id}")

        # Read back the inserted document
        result = collection.find_one({"_id": insert_result.inserted_id})
        print(f"Retrieved document: {result}")

        # Close the MongoDB connection
        client.close()

    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise
    
def test_csv_creation():
    print('working_directory:', os.getcwd())
    print('creating csv')
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6],
        'C': [7, 8, 9]
    })
    df.to_csv('/opt/airflow/dags/error_logs/example.csv', index=False)
    print('CSV file created!')

# Define the DAG
with DAG(
    dag_id='mongo_connection_dag',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # Create a PythonOperator
    mongo_task = PythonOperator(
        task_id='test_csv_creation',
        python_callable=test_csv_creation
    )

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# DAG definition
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
}

with DAG(
    'migration_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    migrate_redis_task = BashOperator(
        task_id='migrate_redis',
        bash_command="""
        # Variables
        RDB_FILE_PATH="/opt/airflow/dags/migration/redis/dump.rdb"
        REDIS_CONTAINER_NAME="airflow-redis-1"
        REDIS_DUMP_DIR="/data"

        # Stop Redis inside the container
        echo "Stopping Redis server inside the container..."
        docker exec $REDIS_CONTAINER_NAME redis-cli shutdown save

        # Copy the .rdb file into the container
        echo "Copying the Redis .rdb file into the container..."
        docker cp $RDB_FILE_PATH $REDIS_CONTAINER_NAME:$REDIS_DUMP_DIR/dump.rdb

        # Restart the Redis container
        echo "Restarting Redis container..."
        docker start $REDIS_CONTAINER_NAME

        # Verify Redis is running
        if docker exec $REDIS_CONTAINER_NAME redis-cli ping | grep -q "PONG"; then
            echo "Redis migration completed successfully."
        else
            echo "Failed to restart Redis with the new .rdb file."
            exit 1
        fi
        """
    )
    
    
    
    migrate_mongodb = BashOperator(
        task_id='migrate_mongodb',
        bash_command="sh /opt/airflow/dags/migration/mongo/migrate_mongo.sh"
    )

    migrate_mongodb 
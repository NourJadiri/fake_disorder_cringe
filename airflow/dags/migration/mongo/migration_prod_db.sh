#!/bin/bash

# filepath: /home/ysidhom/Documents/5IF/adhd_project/mental_health_disorders_analysis/airflow/dags/migration/mongo/migration_mongo.sh

BSON_BACKUP_FILE_PATH="./backup" # Path to BSON backup file inside the container
TARGET_DBS="Ingestion_db" # Array of target database names
MONGO_CONTAINER_NAME="mongo"     # MongoDB container name

# Ensure BSON_BACKUP_FILE_PATH exists
if [ ! -d "$BSON_BACKUP_FILE_PATH" ]; then
  echo "Error: BSON backup file directory '$BSON_BACKUP_FILE_PATH' does not exist!"
  exit 1
fi

echo "Starting MongoDB restore process for databases: ${TARGET_DBS}"

# Step 1: Copy BSON backup file to MongoDB container
echo "Copying BSON backup file to MongoDB container..."
docker cp "$BSON_BACKUP_FILE_PATH" "$MONGO_CONTAINER_NAME:/tmp"

if [ $? -ne 0 ]; then
  echo "Error: Failed to copy BSON file to MongoDB container!"
  exit 1
fi
echo "Successfully copied BSON backup file to MongoDB container."

# Step 2: Restore each database using the BSON file

echo "Restoring database: Production_db from BSON file..."
docker exec -i "$MONGO_CONTAINER_NAME" mongorestore --db Ingestion_db /tmp/backup/Production_db

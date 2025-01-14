#!/bin/bash

# Variables
REDIS_CONTAINER_NAME="airflow-redis-1"          # Name of your Redis container
RDB_FILE_PATH="./dump.rdb"            # Path to your .rdb file (on the host)
CONTAINER_RDB_PATH="/data/dump.rdb"   # Path inside the Redis container
REDIS_DATA_VOLUME="redis-db"          # Name of the Docker volume (optional, only if using named volumes)

# Check if the RDB file exists
if [ ! -f "$RDB_FILE_PATH" ]; then
  echo "Error: RDB file not found at $RDB_FILE_PATH"
  exit 1
fi

echo "Stopping Redis container: $REDIS_CONTAINER_NAME..."
docker stop "$REDIS_CONTAINER_NAME"

# Copy the RDB file to the Redis container's data directory
echo "Copying RDB file to the Redis container..."
docker cp "$RDB_FILE_PATH" "$REDIS_CONTAINER_NAME:$CONTAINER_RDB_PATH"

# Ensure the file is copied correctly
if [ $? -ne 0 ]; then
  echo "Error: Failed to copy RDB file to the Redis container."
  exit 1
fi

# Restart the Redis container
echo "Starting Redis container: $REDIS_CONTAINER_NAME..."
docker start "$REDIS_CONTAINER_NAME"

# Verify if Redis is running
if [ $? -eq 0 ]; then
  echo "Redis container started successfully. Migration complete!"
else
  echo "Error: Failed to start Redis container."
  exit 1
fi

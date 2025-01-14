#!/bin/bash

# Variables
CONTAINER_NAME="mongo"     # Name of your MongoDB container
DBS=("Staging_db" "Ingestion_db" "Production_db")  # List of databases

# Loop through each database and restore
for DB in "${DBS[@]}"; do
  if [ -d "$BACKUP_DIR/$DB" ]; then
    echo "Importing $DB into Docker container..."
    docker exec -i "$CONTAINER_NAME" mongorestore --db "$DB" --drop "./backup/$DB"
    echo "Successfully imported $DB"
  else
    echo "Error: Backup directory $BACKUP_DIR/$DB does not exist"
    exit 1
  fi
done

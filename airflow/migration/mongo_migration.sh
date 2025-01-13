#!/bin/bash

# Ensure MongoDB is running
echo "Waiting for MongoDB to start..."
sleep 5

# Restore the database from the dump
echo "Restoring MongoDB database..."
mongorestore --host localhost --port 27017 --db reddit --drop ./backup/reddit
mongorestore --host localhost --port 27017 --db Ingestion_db --drop ./backup/Ingestion_db
mongorestore --host localhost --port 27017 --db Staging_db --drop ./backup/Staging_db

echo "MongoDB database restored!"
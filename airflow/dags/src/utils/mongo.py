from pymongo import MongoClient


def connect_to_mongo():
    # MongoDB connection details
    mongo_host = 'mongo'  # Docker service name for MongoDB
    mongo_port = 27017

    try:
        # Establish connection to MongoDB
        client = MongoClient(host=mongo_host, port=mongo_port)
        client.list_database_names()
        return True

    except Exception as e:
        print("An error occurred while connecting to MongoDB:", e)
        return False

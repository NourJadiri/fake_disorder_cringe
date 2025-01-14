import os
from dotenv import load_dotenv
import praw
import redis
from pymongo import MongoClient
import pandas as pd
import datetime




def get_month(datetime):
    return datetime.month

def get_year(datetime):
    return datetime.year

def get_utc_time(timestamp):
    # Convert timestamp to UTC datetime
    utc_time = datetime.datetime.utcfromtimestamp(timestamp)
    return utc_time


def connect_to_mongo():
    # Load environment variables from .env file
    os.chdir('../../')      
   
      # MongoDB connection details
    mongo_host = 'mongo'  # Docker service name for MongoDB
    mongo_port = 27017

    try:
        # Establish connection to MongoDB
        client = MongoClient(host=mongo_host, port=mongo_port)

    
        return client
    
    except Exception as e:
        print("An error occurred while connecting to MongoDB:", e)
        raise e


def connect_to_redis():
    try:
        os.chdir('../../')      
        r = redis.Redis(host='redis', port=6379, db=0)
        print("Connected to Redis!")
        return r
    except Exception as e:
        print("An error occurred:", e)
        raise e


def connect_to_reddit():

    # Load environment variables from .env file
    load_dotenv()

    try:
        os.chdir('../../')      
        reddit = praw.Reddit(
            
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD")
        )
        print(f"Connected! Logged in as: {reddit.user.me()}")
        return reddit
    except Exception as e:
        print("An error occurred:", e)
        raise e
    
def test_connections():
    connect_to_mongo()
    connect_to_redis()
    connect_to_reddit()
    print("All connections are working!")

def get_reddit_posts():
    reddit=connect_to_reddit()
    r=connect_to_redis()
    client=connect_to_mongo()
    db=client['Ingestion_db']
    
    if(reddit==None or r==None or client==None):
        print("Connection failed!")
        return None
        
    
    
    Querykeywords=["adhd", "diagnose","energy", "brain", "test", "distracted", "forgetful", "doctor"
                  ,"work","task","disord","struggl","focu","dysfunct","forgot","lazi","prescrib","medic","medicin","pill","self diagnosis","self medication"]
    sortingTechniques=["relevance", "hot", "top", "new", "comments"]

    # Subreddit to target
    subreddit_name = 'ADHD'
    subreddit = reddit.subreddit(subreddit_name)
    posts = []

    Querykeywords=["adhd", "diagnose","energy"]

    for keyword in Querykeywords:
        for sorting in sortingTechniques:
            print("Searching for keyword:", keyword, "using sorting technique:", sorting)
            for post in subreddit.search(query=keyword,sort=sorting,syntax='cloudsearch',time_filter='all',limit=10):# 'hot', 'new', or 'top' post    
                datecreated=get_utc_time(post.created_utc)
                year=datecreated.year
                if(year>2019) and (r.sadd('reddit_posts', post.id)):
                    posts.append({
                    "id":post.id,
                    "title": post.title,
                    "author": str(post.author),
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "upvote_ratio": post.upvote_ratio,
                    "url": post.url,
                    "subreddit": post.subreddit.display_name,
                    "created_at": post.created_utc,
                    "self_text": post.selftext, 
                    "searchQuery":keyword,
                    "staged":0
                })
            
    if(len(posts)==0):
        print("No new posts found!")
        return None
    db.reddit_ingestion.insert_many(posts)
    print
    store_reddit_posts_locally(posts)
    print("Done!")
    #print(posts)
    return None

def test_redis():
    r=connect_to_redis()
    print(r.keys())
    
def test_mongo():
    client=connect_to_mongo()
    if client is None:
        print("Connection failed!")
        return None
    print(client.list_database_names())

def store_reddit_posts_locally(posts):
    # Store the posts in a pandas dataframe
    df = pd.DataFrame(posts)
    outpath="/opt/airflow/dags/src/reddit_posts.csv"
    df.to_csv(outpath, index=False)
    print("Posts stored in reddit_posts.csv")
    return df

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
        document = {"message": "Hello, MongoDB from Airflow!"}
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



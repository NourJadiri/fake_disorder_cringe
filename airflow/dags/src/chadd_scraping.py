import json
import os
from typing import List

import requests
from dotenv import load_dotenv
from ollama import chat, ChatResponse, Client

from pymongo import MongoClient, UpdateOne

from src.chadd.chadd_scrap import ChaddScraper

from src.utils.mongo import *

BASE_URL = 'https://healthunlocked.com'
CONFIG_FILE = 'cookies.json'

def check_cookie_file():
    # Check if the cookie file exists, and if has the required keys
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            cookies_data = json.load(file)
            if 'huSessID' in cookies_data and 'huBv' in cookies_data:
                return True
    return False

def init_chadd_scraper(**context):
    load_dotenv()
    email = os.getenv('CHADD_USERNAME')
    password = os.getenv('CHADD_PASSWORD')

    scraper = ChaddScraper(email= email, password= password, base_url=BASE_URL)
    scraper.login()
    scraper.save_cookies_to_file(filename=CONFIG_FILE)

    print("Cookies saved!")

def clean_ingestion_db_func(**context):
    # Clean the ingestion database
    clean_ingestion_db()
    prepare_ingestion_db()

def clean_staging_db_func(**context):
    # Clean the staging database
    clean_staging_db()

def load_scraper_from_cookies(**context):
    # load the cookies from the file
    scraper = ChaddScraper.from_config(CONFIG_FILE)
    print("Scraper loaded from cookies!")


def fetch_posts_task(**context):
    # Get the cookies from XCom
    scraper = ChaddScraper.from_config(CONFIG_FILE)

    # Fetch posts
    post_ids = scraper.get_posts_ids(start_date='2021-01', end_date='2021-02', community='adult-adhd')
    insert_post_ids(post_ids)

def fetch_members(**context):
    # Get the cookies from XCom
    scraper = ChaddScraper.from_config(CONFIG_FILE)

    # Fetch members
    members = scraper.get_all_members(community='adult-adhd')
    insert_members(members)
    print(members)


def fetch_post_details(**context):
    # delete the cookie file
    os.remove(CONFIG_FILE)

    init_chadd_scraper()
    scraper = ChaddScraper.from_config(CONFIG_FILE)

    # Fetch post details
    post_ids = get_post_ids()
    posts = []
    for post_id in post_ids:
        post = scraper.get_post_details(post_id)
        posts.append(post)

    insert_post_details(posts)

def fetch_members_details(**context):
    # delete the cookie file
    os.remove(CONFIG_FILE)

    init_chadd_scraper()
    scraper = ChaddScraper.from_config(CONFIG_FILE)

    # Fetch post details
    usernames = get_members_usernames()
    members = []
    for username in usernames:
        print('Fetching details for:', username)
        member = scraper.get_user_details(username)
        members.append(member)

    insert_members_details(members)

def infer_gender_from_bio(**context) -> str:
    """
    Infers the gender of members from their bio using the Mistral Completion API.
    Updates the MongoDB documents with the inferred gender.

    Returns:
        str: Summary of the operation.
    """
    # Initialize MongoDB client
    try:
        client = MongoClient('mongo', 27017)
        db = client['chadd_staging_db']
        members_collection = db['members']
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return "Failed to connect to MongoDB."

    # Initialize Mistral client
    try:
        # Test if ollama is running
        # send a request to ollama:11434
        # if it returns 200, then it is running
        req = requests.get('http://ollama:11434')
        client = Client(
            host='http://ollama:11434',
            headers={'x-some-header': 'some-value'}
        )
        print("Initialized llama client successfully.")
    except Exception as e:
        raise ValueError(f"Error initializing Llama client: {e}")

    # Define the query to find documents with gender set to null or empty
    query = {'gender': {'$in': [None, "", "unknown"]}}
    projection = {"bio": 1}  # Only retrieve the bio field

    try:
        documents = list(members_collection.find(query, projection))
        print(f"Found {len(documents)} documents with gender set to null or unknown.")
    except Exception as e:
        print(f"Error fetching documents from MongoDB: {e}")
        return "Failed to fetch documents."

    if not documents:
        return "No documents to update."

    # Prepare bulk operations
    bulk_operations: List[UpdateOne] = []

    for doc in documents:
        bio = doc.get("bio")
        bio = bio.strip() if bio else ""
        member_id = doc.get("_id")

        if not bio:
            inferred_gender = "unknown"
            print(f"Document ID {member_id} has empty bio. Setting gender to 'unknown'.")
        else:
            try:
                response: ChatResponse = client.chat(
                    model='genderizer',
                    messages=[
                        {
                            "role": "user",
                            "content": bio
                        }
                    ]
                )

                inferred_gender = response.message.content

                if inferred_gender not in ["male", "female", "unknown"]:
                    print(f"Unexpected response for Document ID {member_id}: '{inferred_gender}'. Setting to 'unknown'.")
                    inferred_gender = "unknown"
                else:
                    print(f"Inferred gender for Document ID {member_id}: {inferred_gender}.")
            except Exception as e:
                print(f"Error calling Ollama for Document ID {member_id}: {e}. Setting gender to 'unknown'.")
                inferred_gender = "unknown"

        # Prepare the update operation
        bulk_operations.append(
            UpdateOne(
                {"_id": member_id},
                {"$set": {"gender": inferred_gender}}
            )
        )

    # Execute bulk updates
    try:
        if bulk_operations:
            result = members_collection.bulk_write(bulk_operations)
            print(f"Bulk update completed. Matched: {result.matched_count}, Modified: {result.modified_count}.")
            return f"Bulk update completed. Matched: {result.matched_count}, Modified: {result.modified_count}."
        else:
            print("No update operations to perform.")
            return "No updates performed."
    except Exception as e:
        print(f"Error performing bulk update: {e}")
        return "Bulk update failed."

def homogenize_gender(**context) -> None:
    try:
        client = MongoClient('mongo', 27017)
        db = client['chadd_staging_db']
        members_collection = db['members']
        print("Connected to MongoDB successfully.")
    except Exception as e:
        raise ValueError(f"Error connecting to MongoDB: {e}")

    try:
        # Update "woman" to "female"
        result_woman = members_collection.update_many(
            {"gender": "woman"},
            {"$set": {"gender": "female"}}
        )
        print(f"Updated {result_woman.modified_count} documents from 'woman' to 'female'.")

        # Update "man" to "male"
        result_man = members_collection.update_many(
            {"gender": "man"},
            {"$set": {"gender": "male"}}
        )
        print(f"Updated {result_man.modified_count} documents from 'man' to 'male'.")

        # Update all genders not "unknown" to "other"
        result_other = members_collection.update_many(
            {"gender": {"$nin": ["unknown", "male", "female"]}},
            {"$set": {"gender": "other"}}
        )
        print(f"Updated {result_other.modified_count} documents to 'other'.")
    except Exception as e:
        raise ValueError(f"Error updating documents: {e}")

def analyze_sentiment(**context):
    try:
        client = MongoClient('mongo', 27017)
        db = client['chadd_staging_db']
        post_collection = db['posts']
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return "Failed to connect to MongoDB."

    # Initialize Mistral client
    try:
        # Test if ollama is running
        # send a request to ollama:11434
        # if it returns 200, then it is running
        req = requests.get('http://ollama:11434')
        client = Client(
            host='http://ollama:11434',
        )
        print("Initialized llama client successfully.")
    except Exception as e:
        raise ValueError(f"Error initializing Llama client: {e}")

        # Prepare bulk operations
    bulk_operations: List[UpdateOne] = []
    documents = list(post_collection.find())
    for doc in documents:
        body = doc.get("body")
        body = body.strip() if body else ""
        post_id = doc.get("_id")

        if not body:
            inferred_sentiment = "neutral"
            print(f"Document ID {post_id} has empty content. Setting sentiment to 'neutral'.")
        else:
            try:
                response = client.chat(
                    model='sentimentizer',  # Replace with your actual sentiment model name
                    messages=[
                        {
                            "role": "user",
                            "content": body
                        }
                    ]
                )

                inferred_sentiment = response.message.content.strip().lower()

                if inferred_sentiment not in ["positive", "negative", "neutral"]:
                    print(f"Unexpected response for Document ID {post_id}: '{inferred_sentiment}'. Setting to 'neutral'.")
                    inferred_sentiment = "neutral"
                else:
                    print(f"Inferred sentiment for Document ID {post_id}: {inferred_sentiment}.")
            except Exception as e:
                print(f"Error calling Ollama for Document ID {post_id}: {e}. Setting sentiment to 'neutral'.")
                inferred_sentiment = "neutral"

        # Prepare the update operation
        bulk_operations.append(
            UpdateOne(
                {"_id": post_id},
                {"$set": {"sentiment": inferred_sentiment}}
            )
        )

    # Execute bulk updates
    try:
        if bulk_operations:
            result = post_collection.bulk_write(bulk_operations)
            print(f"Bulk update completed. Matched: {result.matched_count}, Modified: {result.modified_count}.")
            return f"Bulk update completed. Matched: {result.matched_count}, Modified: {result.modified_count}."
        else:
            print("No update operations to perform.")
            return "No updates performed."
    except Exception as e:
        print(f"Error performing bulk update: {e}")
        return "Bulk update failed."
import json
import os

from dotenv import load_dotenv
from airflow.models import Variable

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




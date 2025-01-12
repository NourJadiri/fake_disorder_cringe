import json
import os

from dotenv import load_dotenv
from airflow.models import Variable

from src.chadd.chadd_scrap import ChaddScraper

from src.utils.mongo import prepare_ingestion_db, insert_post_ids, clean_ingestion_db

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

def load_scraper_from_cookies(**context):
    # load the cookies from the file
    scraper = ChaddScraper.from_config(CONFIG_FILE)
    print("Scraper loaded from cookies!")


def fetch_posts_task(**context):
    # Get the cookies from XCom
    scraper = ChaddScraper.from_config(CONFIG_FILE)

    # Fetch posts
    post_ids = scraper.get_posts_ids(start_date='2021-01', end_date='2021-02', community='adult-adhd')
    prepare_ingestion_db()
    insert_post_ids(post_ids)

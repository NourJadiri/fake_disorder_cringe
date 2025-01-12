import json
import os

from dotenv import load_dotenv
from airflow.models import Variable

from src.chadd.chadd_scrap import ChaddScraper

BASE_URL = 'https://healthunlocked.com/'
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

    # Load the cookies from the file to push into XCom
    with open(CONFIG_FILE, "r") as file:
        cookies_data = json.load(file)

    # Push cookies into XCom
    context['ti'].xcom_push(key="chadd_cookies", value=cookies_data)

    print("Cookies saved and pushed to XCom!")


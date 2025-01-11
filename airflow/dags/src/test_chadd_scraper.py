# load email and password from .env
import os
from dotenv import load_dotenv

from chadd_scrap import ChaddScraper

load_dotenv()
email = os.getenv('CHADD_USERNAME')
password = os.getenv('CHADD_PASSWORD')


chadd_scraper = ChaddScraper(
    email = email,
    password = password,
    base_url = 'https://healthunlocked.com/'
)

chadd_scraper.login()


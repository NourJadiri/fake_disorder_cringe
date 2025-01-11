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

posts = []

def test_chadd_scraper_login():
    chadd_scraper.login()

    assert chadd_scraper.huSessID is not None
    assert chadd_scraper.huBv is not None


def test_get_posts_ids():
    post_ids = chadd_scraper.get_posts_ids(start_date='2020-01', end_date='2020-02', community='adult-adhd')
    assert len(post_ids) > 0
    assert all(isinstance(post_id, int) for post_id in post_ids)


def test_get_post_details():
    post_id = 151579120
    post = chadd_scraper.get_post_details(post_id)
    assert isinstance(post, dict)
    assert post.get('id') == post_id

# runnig the tests
test_chadd_scraper_login()
test_get_posts_ids()
test_get_post_details()



# load email and password from .env
import os
from dotenv import load_dotenv

from chadd.models.post import Post
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

postIds = chadd_scraper.get_posts_ids(start_date='2020-01', end_date='2020-02', community='adult-adhd')

posts = []

for post_id in postIds:
    post_details = chadd_scraper.get_post_details(post_id, community='adult-adhd')
    new_post = Post.from_json(post_details)
    print(new_post.title)


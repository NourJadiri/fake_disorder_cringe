from datetime import timedelta, datetime

import requests
import json
import os

from chadd.models.user import User
from chadd.models.post import Post


class ChaddScraper:
    def __init__(self, email: str, password: str, base_url: str):
        """
        Initialize the scraper with user credentials and the base URL of the website.

        :param email: Your login email
        :param password: Your login password
        :param base_url: The base URL of the website (e.g. 'https://healthunlocked.com/')
        """
        self.email = email
        self.password = password
        self.base_url = base_url

        # A requests.Session object will help persist cookies between requests
        self.session = requests.Session()

        # We’ll store these cookie values as class attributes after login
        self.AWSALB = None
        self.AWSALBCORS = None
        self.huBv = None
        self.huLang = None
        self.huSessID = None

    def login(self) -> None:
        """
        Log in to the website by sending a POST request to the /session route with
        the provided credentials. Extract and store relevant cookies if login is successful.
        """
        login_url = f"{self.base_url}/session"

        # Prepare the form data, matching the input names from the login page
        payload = {
            "username": self.email,
            "password": self.password
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://healthunlocked.com",
            "Referer": "https://healthunlocked.com/login",
            "Sec-CH-UA": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36",
            "Baggage": "sentry-environment=production,sentry-public_key=16a8291a236a41fe8f36d3fd90c09774,sentry-trace_id=c33adb5e575b47cd96a561664e26b36e",
            "Sentry-Trace": "c33adb5e575b47cd96a561664e26b36e-a3202bce4bdff1ef"
        }

        self.session.headers.update(headers)
        # Send the POST request to the login endpoint
        response = self.session.post(login_url, json=payload)

        if response.status_code != 200:
            print(response.text)
            raise Exception("Login failed with status code:", response.status_code)

        print("Extracting cookies...")
        # Extract cookies from the session. We only store the ones needed.
        for cookie in self.session.cookies:
            print(f"Cookie: {cookie.name}, Value: {cookie.value}")
            if cookie.name == "huBv":
                self.huBv = cookie.value
            elif cookie.name == "huLang":
                self.huLang = cookie.value
            elif cookie.name == "huSessID":
                self.huSessID = cookie.value

        print("Login successful! 😊😊")


    def save_cookies_to_file(self, filename: str = "cookies.json") -> None:
        """
        Persist the currently stored cookies to a local JSON file so that they
        can be reused for another session without requiring a new login.

        :param filename: Name of the JSON file where cookies will be saved
        """
        cookies_data = {
            "huBv": self.huBv,
            "huSessID": self.huSessID
        }

        with open(filename, "w") as f:
            json.dump(cookies_data, f)

    def load_cookies_from_file(self, filename: str = "cookies.json") -> None:
        """
        (Optional) Load previously saved cookies from a local JSON file.
        This method can be handy if you want to avoid logging in again.

        :param filename: Name of the JSON file where cookies are stored
        """
        if os.path.exists(filename):
            with open(filename, "r") as f:
                cookies_data = json.load(f)

            # Update the class attributes
            self.huBv = cookies_data.get("huBv", None)
            self.huSessID = cookies_data.get("huSessID", None)

            # Also update the session’s cookie jar for subsequent requests
            for name, value in cookies_data.items():
                if value is not None:
                    self.session.cookies.set(name, value)
        else:
            print(f"No cookie file found at {filename}. Please log in first.")

    def get_posts_ids(self, start_date = '2017-07', end_date = '2025-01', community = 'adult-adhd') -> list:
        """
        Get all the posts ids for a given community and a given range of years and months.

        :param community: The community for which we want to get the posts
        :param start_date: The start date of the range
        :param end_date: The end date of the range
        :return: A list of posts ids
        """

        if not self.huSessID:
            raise Exception("Please log in first. Execute ChaddScraper.login() first.")

        posts_ids = []
        base_url = f"{self.base_url}/private/posts/{community}/latest?"

        start_date = datetime.strptime(start_date, "%Y-%m")
        end_date = datetime.strptime(end_date, "%Y-%m")

        if start_date > end_date:
            raise Exception("Start date must be before end date.")

        current_date = start_date
        while current_date <= end_date:
            year = current_date.year
            month = current_date.month

            print(f"Fetching posts for {year}-{month}...")

            url = f"{base_url}year={year}&month={month}"
            response = self.session.get(url)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch posts for {year}-{month}")

            try:
                data = response.json()
                posts_ids.extend(post['postId'] for post in data if "postId" in post)

            except Exception as e:
                print(f"Error processing response for {year}-{month}: {e}")

            next_month = current_date.replace(day=28) + timedelta(days=4)
            current_date = next_month.replace(day=1)

        return posts_ids

    def get_post_details(self, post_id, community = 'adult-adhd') -> Post:
        """
        Get the details of a post given its ID.

        :param post_id: The ID of the post
        :param community: The community of the post
        :return: A dictionary containing the post details
        """
        if not self.huSessID:
            raise Exception("Please log in first. Execute ChaddScraper.login() first.")

        url = f"{self.base_url}/private/posts/{community}/{post_id}"
        response = self.session.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch post details for post ID {post_id}")

        post_object = response.json()
        return Post.from_json(post_object)

    @staticmethod
    def save_post_to_file(post: Post, filename: str = "post.json") -> None:
        """
        Save a single post to a local JSON file.

        :param post: The post to save
        :param filename: The name of the JSON file where the post will be saved
        """
        with open(filename, "w") as f:
            json.dump(post.to_dict(), f)

    @staticmethod
    def save_posts_to_file(posts: list[Post], filename: str = "posts.json") -> None:
        """
        Save the list of posts to a local JSON file.

        :param posts: The list of posts to save
        :param filename: The name of the JSON file where posts will be saved
        """
        with open(filename, "w") as f:
            json.dump([post.to_dict() for post in posts], f)


    def get_user_details(self, username):
        """
        Get the details of a user given their username.

        :param username: The username of the user
        :return: A dictionary containing the user details
        """
        if not self.huSessID:
            raise Exception("Please log in first. Execute ChaddScraper.login() first.")

        url = f"{self.base_url}/private/user/profile/{username}"
        response = self.session.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch user details for username {username}")

        user_object = response.json()
        user = User.from_json(user_object)
        return user

    @staticmethod
    def save_users_to_file(users: list[User], filename: str = "users.json") -> None:
        """
        Save the list of users to a local JSON file.

        :param users: The list of users to save
        :param filename: The name of the JSON file where users will be saved
        """
        with open(filename, "w") as f:
            json.dump([user.to_dict() for user in users], f)

    def get_members_for_page(self, page, community='adult-adhd'):
        """
        Get the members of a community for a given page.

        :param page: The page number
        :param community: The community for which we want to get the members
        :return: A list of usernames
        """
        if not self.huSessID:
            raise Exception("Please log in first. Execute ChaddScraper.login() first.")

        limit = 12
        base_url = f"{self.base_url}/private/members/{community}"
        url = f"{base_url}?limit={limit * page}"

        print(f"Fetching members for page {page}...")
        return self._fetch_members_for_page(url)


    def get_all_members(self, community='adult-adhd'):
        """
        Get all the members of a community.

        :param community: The community for which we want to get the members
        :return: A list of usernames
        """
        if not self.huSessID:
            raise Exception("Please log in first. Execute ChaddScraper.login() first.")

        limit = 12
        base_url = f"{self.base_url}/private/members/{community}"

        # Fetch total number of members
        total_members = self.session.get(base_url).json().get('total', 0)
        total_pages = total_members // limit + (1 if total_members % limit != 0 else 0)

        members = []
        for page in range(1, total_pages + 1):
            url = f"{base_url}?limit={limit * page}"
            members.extend(self._fetch_members_for_page(url))

        print(f"Total members fetched: {len(members)}")
        return members


    def _fetch_members_for_page(self, url):
        """
        Helper method to fetch members for a given URL.

        :param url: The URL to fetch members from
        :return: A list of usernames
        """
        response = self.session.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch members from {url}")

        try:
            data = response.json()
            return [member['username'] for member in data.get('members', []) if "username" in member]
        except Exception as e:
            print(f"Error processing response from {url}: {e}")
            return []


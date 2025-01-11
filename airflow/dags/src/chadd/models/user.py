from typing import List, Optional
from datetime import datetime

class User:
    def __init__(self,
                 user_id: int,
                 username: str,
                 age: Optional[int] = None,
                 gender: Optional[str] = None,
                 country: Optional[str] = None,
                 bio: Optional[str] = None):
        self.user_id = user_id
        self.username = username
        self.age = age
        self.gender = gender
        self.country = country
        self.bio = bio

    def __repr__(self):
        return f"Author(id={self.user_id}, username={self.username}, age={self.age}, gender={self.gender}, country={self.country})"

    def to_dict(self):
        return {
            "author_id": self.user_id,
            "username": self.username,
            "age": self.age,
            "gener": self.gender,
            "country": self.country,
            "bio": self.bio
        }
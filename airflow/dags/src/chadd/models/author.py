from typing import List, Optional
from datetime import datetime

class Author:
    def __init__(self,
                 author_id: int,
                 username: str,
                 age: Optional[int] = None,
                 gender: Optional[str] = None,
                 country: Optional[str] = None,
                 bio: Optional[str] = None):
        self.author_id = author_id
        self.username = username
        self.age = age
        self.gender = gender
        self.country = country
        self.bio = bio

    def __repr__(self):
        return f"Author(id={self.author_id}, username={self.username}, age={self.age}, gender={self.gender}, country={self.country})"

    def to_dict(self):
        return {
            "author_id": self.author_id,
            "username": self.username,
            "age": self.age,
            "gener": self.gender,
            "country": self.country,
            "bio": self.bio
        }
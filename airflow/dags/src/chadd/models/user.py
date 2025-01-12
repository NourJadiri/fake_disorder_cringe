from typing import List, Optional
from datetime import datetime

from src.chadd.models.condition import Condition


class User:
    def __init__(self,
                 user_id: int,
                 username: str,
                 age: Optional[int] = None,
                 gender: Optional[str] = None,
                 country: Optional[str] = None,
                 bio: Optional[str] = None,
                 conditions: Optional[List[Condition]] = None):
        self.user_id = user_id
        self.username = username
        self.age = age
        self.gender = gender
        self.country = country
        self.bio = bio
        self.conditions = conditions or []

    def __repr__(self):
        return f"User(id={self.user_id}, username={self.username}, age={self.age}, gender={self.gender}, country={self.country}, bio={self.bio}, conditions={self.conditions})"

    @classmethod
    def from_json(cls, api_response: dict) -> 'User':
        basics = api_response.get("basics", {})
        profile = api_response.get("profileUser", {})
        conditions = api_response.get("conditions", [])
        return cls(
            user_id=profile.get("userId"),
            username=profile.get("username"),
            gender=basics.get("gender"),
            country=basics.get("country"),
            bio=basics.get("aboutMe", None),
            conditions=[Condition.from_json(condition) for condition in conditions]
        )


    def to_dict(self):
        return {
            "author_id": self.user_id,
            "username": self.username,
            "age": self.age,
            "gender": self.gender,
            "country": self.country,
            "bio": self.bio,
            "conditions": [condition.to_dict() for condition in self.conditions]
        }
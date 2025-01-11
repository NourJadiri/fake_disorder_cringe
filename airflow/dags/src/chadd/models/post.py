from datetime import datetime
from typing import Optional, List

from chadd.models.response import Response
from chadd.models.user import User


class Post:
    def __init__(self,
                 post_id: int,
                 title: str,
                 body: str,
                 author: User,
                 date_created: datetime,
                 total_responses: int,
                 responses: Optional[List[Response]] = None):
        self.post_id = post_id
        self.title = title
        self.body = body
        self.author = author
        self.date_created = date_created
        self.total_responses = total_responses
        self.responses = responses or []

    def __repr__(self):
        return f"Post(id={self.post_id}, title={self.title}, author={self.author}, date_created={self.date_created}, total_responses={self.total_responses})"

    @classmethod
    def from_json(cls, api_response: dict) -> 'Post':
        author_data = api_response.get("author", {})
        author = User(
            user_id=author_data.get("id"),
            username=author_data.get("username"),
            age=author_data.get("age"),
            gender=author_data.get("gender"),
            country=author_data.get("country"),
            bio=author_data.get("bio"),
        )

        responses = []
        for response_data in api_response.get("responses", []):
            response_author_data = response_data.get("author", {})
            response_author = User(
                user_id=response_author_data.get("id"),
                username=response_author_data.get("username"),
                age=None,  # Response authors might not have detailed demographics
                gender=None,
                country=None,
                bio=None,
            )
            responses.append(
                Response(
                    response_id=response_data.get("id"),
                    author=response_author,
                    body=response_data.get("body"),
                    date_created=datetime.strptime(response_data.get("dateCreated"), "%Y-%m-%dT%H:%M:%S.%fZ"),
                )
            )

        return cls(
            post_id=api_response.get("id"),
            title=api_response.get("title"),
            body=api_response.get("body"),
            author=author,
            date_created=datetime.strptime(api_response.get("dateCreated"), "%Y-%m-%dT%H:%M:%S.%fZ"),
            total_responses=api_response.get("totalResponses", 0),
            responses=responses,
        )

    def to_dict(self) -> dict:
        return {
            "post_id": self.post_id,
            "title": self.title,
            "body": self.body,
            "author": self.author.to_dict(),
            "date_created": self.date_created.isoformat(),
            "total_responses": self.total_responses,
            "responses": [response.to_dict() for response in self.responses],
        }
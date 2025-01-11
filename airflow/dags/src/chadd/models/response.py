from datetime import datetime

from chadd.models.user import User


class Response:
    def __init__(self,
                 response_id: int,
                 author: User,
                 body: str,
                 date_created: datetime):
        self.response_id = response_id
        self.author = author
        self.body = body
        self.date_created = date_created

    def __repr__(self):
        return f"Response(id={self.response_id}, author={self.author}, date_created={self.date_created})"

    def to_dict(self):
        return {
            "response_id": self.response_id,
            "author": self.author.username,
            "body": self.body,
            "date_created": self.date_created.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
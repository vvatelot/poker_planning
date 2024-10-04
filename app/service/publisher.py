import json
from functools import lru_cache
from typing import Any

import jwt
from pymercure.message import Message
from pymercure.publisher.sync import SyncPublisher

from app.config import Settings


class Publisher:
    def __init__(self, room_id: str):
        jwt_token = jwt.encode(
            payload={"mercure": {"publish": [f"room/{room_id}"]}},
            key=Settings().mercure_publisher_jwt_key,
        )
        self._publisher = SyncPublisher(
            Settings().mercure_host,
            jwt_token,
        )
        self.room_id = room_id

    def publish(self, event: str, data: Any):
        self._publisher.publish(
            Message(
                topics=[f"room/{self.room_id}"],
                data=json.dumps({"event": event, "data": data}),
            )
        )


@lru_cache
def get_publisher(room_id: str) -> Publisher:
    return Publisher(room_id)

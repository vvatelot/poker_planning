from typing import Annotated

from pydantic import BaseModel, Field


class Vote(BaseModel):
    value: int | None = None
    ready: bool = False


class User(BaseModel):
    id: str
    name: Annotated[str, Field(max_length=50)]
    vote: Vote = Vote()

    def get_user(self, ready: bool = False) -> dict[str, str]:
        if ready:
            return self.model_dump()

        self.vote.value = None

        return self.model_dump()


class Room(BaseModel):
    name: Annotated[str, Field(max_length=50)]
    owner: str
    show: bool = False
    users: list[User] = []

import os

from aiofiles import open as aiopen  # type: ignore

from app.models import Room


async def get_room(room_id: str) -> Room:
    async with aiopen(f"data/rooms/{room_id}.json", "r") as f:
        return Room.model_validate_json(await f.read())


async def save_room(room_id: str, room: Room) -> None:
    async with aiopen(f"data/rooms/{room_id}.json", "w") as f:
        await f.write(room.model_dump_json())


async def delete_room(room_id: str) -> None:
    os.remove(f"data/rooms/{room_id}.json")

import statistics

from app.models import Room, User
from app.repository.room import delete_room, get_room, save_room
from app.service.giphy import get_gif
from app.service.publisher import Publisher


async def handle_user_event(publisher: Publisher, room_id: str, user: User):
    room = await get_room(room_id)

    if user.id not in [u.id for u in room.users]:
        room.users.append(user)

    else:
        room.users = [u if u.id != user.id else user for u in room.users]

    await save_room(room_id, room)

    publisher.publish(
        event="users",
        data=[user.get_user(ready=room.show) for user in room.users],
    )


async def handle_user_leave_event(publisher: Publisher, room_id: str, user_id: str):
    room = await get_room(room_id)

    room.users = [u for u in room.users if u.id != user_id]

    if len(room.users) == 0:
        await delete_room(room_id)
    else:
        await save_room(room_id, room)

    publisher.publish(
        event="users",
        data=[user.get_user(ready=room.show) for user in room.users],
    )


async def handle_vote_event(
    publisher: Publisher, room_id: str, user_id: str, vote: int
):
    room = await get_room(room_id)
    try:
        user = next(u for u in room.users if u.id == user_id)
        user.vote.value = vote
        user.vote.ready = True
    except StopIteration:
        print(f"user not found {user_id}", [u for u in room.users])

    await save_room(room_id, room)

    publisher.publish(
        event="votes",
        data=[user.get_user(ready=room.show) for user in room.users],
    )


async def average_votes(room: Room) -> float:
    return round(
        sum([user.vote.value if user.vote.value else 0 for user in room.users])
        / len([user for user in room.users if user.vote.value]),
        2,
    )


async def handle_reveal_vote_event(publisher: Publisher, room_id: str, user_id: str):
    room = await get_room(room_id)

    try:
        variance = statistics.variance(
            [user.vote.value for user in room.users if user.vote.value]
        )
    except statistics.StatisticsError:
        variance = 0

    room.show = True

    await save_room(room_id, room)
    gif_url, gif_tag = await get_gif(variance)

    publisher.publish(
        event="reveal_votes",
        data={
            "users": [user.get_user(ready=True) for user in room.users],
            "average": await average_votes(room),
            "gif_url": gif_url,
            "gif_tag": gif_tag,
            "variance": variance,
        },
    )


async def handle_reset_votes_event(publisher: Publisher, room_id: str, user_id: str):
    room = await get_room(room_id)

    room.show = False

    for user in room.users:
        user.vote.value = None
        user.vote.ready = False

    await save_room(room_id, room)

    publisher.publish(
        event="reset_votes",
        data=[user.get_user(ready=room.show) for user in room.users],
    )

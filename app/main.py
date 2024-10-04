import uuid
from typing import Annotated

import jwt
from fastapi import (
    Body,
    Cookie,
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import Settings
from app.config.template import get_templates
from app.models import Room, User
from app.service.publisher import get_publisher
from app.service.room import (
    handle_reset_votes_event,
    handle_reveal_vote_event,
    handle_user_event,
    handle_user_leave_event,
    handle_vote_event,
)

app = FastAPI(debug=False)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if (
        exc.status_code == status.HTTP_404_NOT_FOUND
        and "text/html" in request.headers.get("accept", "")
    ):
        templates = get_templates()
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            status_code=404,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.get("/")
async def home(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"title": "Poker Planning"}
    )


@app.post("/")
async def create_room(
    request: Request,
    room_name: Annotated[str, Form()],
    user_id: Annotated[str, Form()],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
):
    room_id = uuid.uuid4()

    with open(f"data/rooms/{room_id}.json", "w") as f:
        f.write(Room(name=room_name, owner=user_id).model_dump_json())

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Poker Planning", "room_id": room_id},
    )


@app.get("/{room_id}")
async def get_room_detail(
    request: Request,
    room_id: str,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    user_id: Annotated[str | None, Cookie()] = None,
):
    try:
        with open(f"data/rooms/{room_id}.json", "r") as f:
            room = Room.model_validate_json(f.read())
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    response = templates.TemplateResponse(
        request=request,
        name="room.html",
        context={
            "room_id": room_id,
            "title": f"Poker Planning - {room.name}",
            "name": room.name,
            "users": [user.get_user(ready=False) for user in room.users],
            "is_owner": room.owner == user_id,
            "mercure_host": Settings().mercure_host_frontend,
        },
    )

    response.set_cookie(
        key="mercureAuthorization",
        value=jwt.encode(
            payload={"mercure": {"subscribe": [f"room/{room_id}"]}},
            key=Settings().mercure_subscriber_jwt_key,
        ),
        path="/.well-known/mercure",
        secure=True,
    )

    return response


@app.post("/room/{room_id}/votes")
async def add_a_new_vote(
    room_id: str,
    vote: int,
    user_id: Annotated[str, Cookie()],
):
    publisher = get_publisher(room_id)

    await handle_vote_event(
        publisher=publisher, room_id=room_id, user_id=user_id, vote=vote
    )


@app.post("/room/{room_id}/actions")
async def make_an_action(
    room_id: str,
    action: str,
    user_id: Annotated[str, Cookie()],
):
    publisher = get_publisher(room_id)

    if action == "reset":
        await handle_reset_votes_event(
            publisher=publisher, room_id=room_id, user_id=user_id
        )

    if action == "show":
        await handle_reveal_vote_event(
            publisher=publisher, room_id=room_id, user_id=user_id
        )


@app.delete("/room/{room_id}/users")
async def remove_user(
    room_id: str,
    user_id: Annotated[str, Cookie()],
):
    publisher = get_publisher(room_id)

    await handle_user_leave_event(publisher=publisher, room_id=room_id, user_id=user_id)


@app.post("/room/{room_id}/users")
async def add_user(
    room_id: str,
    user_name: Annotated[str, Body()],
    user_id: Annotated[str, Cookie()],
):
    publisher = get_publisher(room_id)

    await handle_user_event(
        publisher=publisher, room_id=room_id, user=User(name=user_name, id=user_id)
    )

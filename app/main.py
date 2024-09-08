import uuid
from typing import Annotated

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import Settings
from app.config.template import get_templates
from app.models import Room, User
from app.service.room import (
    handle_reset_votes_event,
    handle_reveal_vote_event,
    handle_user_event,
    handle_user_leave_event,
    handle_vote_event,
)
from app.ws import manager

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
async def room_detail(
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

    return templates.TemplateResponse(
        request=request,
        name="room.html",
        context={
            "room_id": room_id,
            "title": f"Poker Planning - {room.name}",
            "name": room.name,
            "users": [user.model_dump() for user in room.users],
            "is_owner": room.owner == user_id,
            "websocket_host": Settings().websocket_host,
        },
    )


@app.websocket("/room/{room_id}/users/{user_id}")
async def websocket_users(websocket: WebSocket, room_id: str, user_id: str):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            match data["event"]:
                case "user":
                    await handle_user_event(
                        manager, room_id, User.model_validate(data["user"])
                    )
                case "vote":
                    await handle_vote_event(manager, room_id, user_id, data["vote"])
                case "reset_votes":
                    await handle_reset_votes_event(manager, room_id, user_id)
                case "reveal_votes":
                    await handle_reveal_vote_event(manager, room_id, user_id)
                case _:
                    pass

    except WebSocketDisconnect:
        await handle_user_leave_event(manager, room_id, user_id, websocket)

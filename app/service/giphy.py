from random import choice

import httpx

from app.config import Settings


async def get_gif_by_tag(tag: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.giphy.com/v1/gifs/random",
                params={
                    "api_key": Settings().giphy_api_key,
                    "tag": tag,
                    "rating": "g",
                },
            )

            data = response.json()

        return data["data"]["images"]["fixed_height"]["url"]
    except Exception:
        return ""


async def get_gif(variance: float) -> tuple[str, str]:
    if variance < 0.5:
        tag = choice(["excited", "high five", "celebrate"])
        return await get_gif_by_tag(tag), tag
    elif variance < 1:
        tag = choice(["happy", "good job", "congratulations"])
        return await get_gif_by_tag(tag), tag
    elif variance < 5:
        tag = choice(["neutral", "meh", "shrug"])
        return await get_gif_by_tag(tag), tag
    elif variance < 10:
        tag = choice(["sad", "disappointed", "facepalm"])
        return await get_gif_by_tag(tag), tag
    else:
        tag = choice(["angry", "nope", "frustrated"])
        return await get_gif_by_tag(tag), tag

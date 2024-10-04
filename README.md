# Poker Planning

This is a simple poker planning tool for remote teams. It is a web application that allows users to create a room and join it with a unique code. Once in the room, users can vote on a story point for a task. The results are shown in real-time.

## Technologies

- [Fastapi](https://fastapi.tiangolo.com/)
- [Mercure](https://mercure.rocks/)
- [Alpine.js](https://alpinejs.dev/)
- [Bulma.io](https://bulma.io/)

## Requirements

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/)
- [Docker compose](https://docs.docker.com/compose/)
- [Taskfile](https://taskfile.dev/#/installation)

> This project can be run with devcontainers in Visual Studio Code.

## Settings

The application uses environment variables to configure the settings. You can set the following variables:

- `GIPHY_API_KEY`: The Giphy API key to fetch gifs. If not provided, the application will not fetch gifs.
- `APP_HOST`: The host where the application will run. Default is `localhost:8000`.
- `APP_PORT`: The port where the application will run. Default is `8000`.
- `APP_SCHEME`: The scheme used by the application. Default is `http`.
- `MERCURE_HOST`: The host where the Mercure hub will run. Default is `http://mercure:80/.well-known/mercure`.
- `MERCURE_HOST_FRONTEND`: The host where the Mercure hub will run, view from the frontend. Default is `http://localhost:3000/.well-known/mercure`.
- `MERCURE_PORT`: The port where the Mercure hub will run. Default is `3000`
- `MERCURE_PUBLISHER_JWT_KEY`: The key used to sign the JWT token for the publisher. Default is `!ChangeThisMercureHubJWTSecretKey!`.
- `MERCURE_SUBSCRIBER_JWT_KEY`: The key used to sign the JWT token for the subscriber. Default is `!ChangeThisMercureHubJWTSecretKey!`.

## How to run

First, you need to clone the repository:

```bash
git clone 
```

### Docker compose

1. Run `docker-compose up --build`
2. Open your browser and go to `http://localhost:8000`

### Local

1. Install the dependencies with `uv sync --frozen`
2. Run the application with `task dev-start`
3. Open your browser and go to `http://localhost:8000`

## How to use

1. Create a room by clicking on the `Create room` button
2. Share the room code with your team
3. Vote on a story point
4. See the results in real-time :tada:

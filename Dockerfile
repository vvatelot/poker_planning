FROM python:3-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY . .
RUN uv sync --frozen
RUN uv add granian

# CMD ["uv", "run", "uvicorn",  "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"]
CMD ["uv", "run", "granian", "--interface", "asgi", "app.main:app","--host", "0.0.0.0",  "--port", "8000", "--workers", "1"]
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    giphy_api_key: str = ""
    websocket_host: str = "ws://localhost:8000"

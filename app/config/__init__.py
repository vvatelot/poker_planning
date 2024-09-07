from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = "localhost:8000"
    giphy_api_key: str = ""
    websocket_protocol: str = "ws"

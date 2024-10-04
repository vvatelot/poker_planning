from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    giphy_api_base_url: str = "https://api.giphy.com/v1/gifs"
    giphy_api_key: str = ""
    mercure_host: str = "http://localhost:3000/.well-known/mercure"
    mercure_host_frontend: str = "http://localhost:3000/.well-known/mercure"
    mercure_publisher_jwt_key: str = "!ChangeThisMercureHubJWTSecretKey!"
    mercure_subscriber_jwt_key: str = "!ChangeThisMercureHubJWTSecretKey!"

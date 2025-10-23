from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    google_api_key: 
    db_connection_string: str

    class Config:
        env_file = ".env"

settings = Settings()

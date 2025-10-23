from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    google_api_key: "AIzaSyDc1wm58d_a5Ng1XqcyaDlq2QaACadyVro"
    db_connection_string: str

    class Config:
        env_file = ".env"

settings = Settings()

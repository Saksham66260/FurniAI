
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://furniai:furniai@localhost:5432/furniai"
    redis_url: str = "redis://localhost:6379/0"
    groq_api_key: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost:4173"

    model_config = SettingsConfigDict(env_file=".env")
    
settings = Settings()

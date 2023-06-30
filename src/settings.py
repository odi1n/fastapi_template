from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"

    DEBUG: bool = Field(env="DEBUG")
    HOST: str = Field("127.0.0.1", env="HOST")
    PORT: int = Field(8000, env="PORT")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


setting = get_settings()

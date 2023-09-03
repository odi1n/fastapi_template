from functools import lru_cache
from typing import Any, Dict, Optional, no_type_check

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"

    DEBUG: bool = Field(env="DEBUG")
    HOST: str = Field("127.0.0.1", env="HOST")
    PORT: int = Field(8000, env="PORT")

    DB_DIALECT: str = Field("postgresql+asyncpg", env="DB_DIALECT")
    DB_HOST: str = Field("127.0.0.1", env="DB_HOST")
    DB_PORT: int = Field(5432, env="DB_PORT")
    DB_NAME: str = Field(env="DB_NAME")
    DB_USER: str = Field(env="DB_USER")
    DB_PASSWORD: str = Field(env="DB_PASSWORD")
    DB_DSN: Optional[str] = Field(None, env="DB_DSN")

    JWT_ALGORITHM: str = Field(env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(
        env="JWT_REFRESH_TOKEN_EXPIRE_MINUTES",
    )
    JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = Field(env="JWT_REFRESH_SECRET_KEY")

    @no_type_check
    @field_validator("DB_DSN")
    def assemble_db_dsn(
        cls,
        value: Optional[str],
        values: Dict[str, Any],
    ) -> str:
        if isinstance(value, str):
            return value

        db_uri = PostgresDsn.build(
            scheme=values.data.get("DB_DIALECT"),
            username=values.data.get("DB_USER"),
            password=values.data.get("DB_PASSWORD"),
            host=values.data.get("DB_HOST"),
            port=values.data.get("DB_PORT"),
            path=f"{values.data.get('DB_NAME') or ''}",
        )
        return db_uri.unicode_string()


@lru_cache()
def get_settings() -> Settings:
    return Settings()


setting = get_settings()

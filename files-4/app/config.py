from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    RAILWAY_TOKEN: str = ""
    ALLOWED_ORIGINS: str = "http://localhost:8081"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()

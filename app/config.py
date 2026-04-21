from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"


ADMIN_MAX_DISCOUNT_PERCENT = 20
MANAGER_MAX_DISCOUNT_PERCENT = 10

settings = Settings()
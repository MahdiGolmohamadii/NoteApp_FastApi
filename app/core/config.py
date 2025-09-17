from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict

class Settings(BaseSettings):
    DB_URL: str
    SECRETE_KEY: str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=".env",
        from_attributes=True  # orm_mode is now from_attributes
    )


settings = Settings()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str
    SECRETE_KEY: str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config():
        env_file = ".env"
        orm_mode = True


settings = Settings()
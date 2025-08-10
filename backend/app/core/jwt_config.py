
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


class Settings(BaseSettings):
    
    load_dotenv()

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

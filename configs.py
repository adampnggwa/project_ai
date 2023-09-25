from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Config(BaseSettings):
    api_key_openai: str = Field(os.environ.get("API_KEY_OPENAI", "default_value"))
    redirect_uri_register: str = Field(os.environ.get("REDIRECT_URI_REGISTER", "default_value"))
    redirect_uri_login: str = Field(os.environ.get("REDIRECT_URI_LOGIN", "default_value"))
    database_connections: str = Field(os.environ.get("DATABASE_CONNECTIONS", "default_value"))

config = Config()
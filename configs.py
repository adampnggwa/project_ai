from pydantic import Field
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    api_key_openai: str = Field("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")
    redirect_uri_register: str = Field("https://4706-149-108-13-248.ngrok-free.app/auth2callbackRegister")
    redirect_uri_login: str = Field("https://4706-149-108-13-248.ngrok-free.app/auth2callbackLogin")
    database_connections: str = Field("mysql://root:@127.0.0.1/ai_image")
    
config = Config()

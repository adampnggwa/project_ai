from pydantic import BaseModel, HttpUrl

class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    token: str
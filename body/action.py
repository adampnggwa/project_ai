from pydantic import BaseModel

class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
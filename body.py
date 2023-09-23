from pydantic import BaseModel

class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    token: str

class EditImageRequest(BaseModel):
    prompt: str
    image_url: str
    token: str  

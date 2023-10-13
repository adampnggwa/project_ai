from pydantic import BaseModel
from typing import Optional
class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
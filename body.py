from pydantic import BaseModel, HttpUrl

class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    token: str

class ImageEditRequest(BaseModel):
    image: HttpUrl  # URL gambar yang akan diedit
    mask: HttpUrl   # URL masker untuk gambar
    prompt: str
    token: str
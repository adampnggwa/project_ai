from pydantic import BaseModel
from typing import Optional

class EditProfileRequest(BaseModel):
    password: str
    new_email: Optional[str] = None
    new_password: Optional[str] = None

class DeleteAccountRequest(BaseModel):
    email: str
    password: str
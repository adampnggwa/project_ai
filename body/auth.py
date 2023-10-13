from typing import Optional
from pydantic import BaseModel

class signupORsignin(BaseModel):
    email: Optional[str]
    password: Optional[str]

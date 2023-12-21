from pydantic import BaseModel
from typing import Optional

class EditProfileRequest(BaseModel):
    password: str
    new_email: Optional[str] = None
    new_password: Optional[str] = None

class DeleteAccountRequest(BaseModel):
    email: str
    password: str

class BuyerDataRequest(BaseModel):
    first_name: str
    last_name: str
    address_line: str
    city: str
    region: str
    postcode: str
    country: str

class PaymentRequest(BaseModel):
    payment_amount: float
    payment_method: str
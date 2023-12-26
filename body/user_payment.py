from pydantic import BaseModel

class BuyerDataRequest(BaseModel):
    first_name: str
    last_name: str
    address_line: str
    city: str
    region: str
    postcode: str
    country: str
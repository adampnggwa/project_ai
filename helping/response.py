from typing import Optional
from database.model import accesstoken
 
async def access_token_response(user_id):
    data = await accesstoken.filter(user_id=user_id).first()
    return{
        'token': str(data.token),
        'token_expiration': str(data.token_expiration)
    }

def pesan_response(message: str, email: Optional[str]='anonymus'):
    return{
        'email': email,
        'message': message
    }

async def response_user(user):
    access_token_data = await accesstoken.filter(user_id=user.user_id).first()  
    if access_token_data:
        response = {
            "user_id": str(user.user_id),
            "email": user.email,
            "token": str(access_token_data.token),
            "token_expiration": str(access_token_data.token_expiration),
            "points": str(user.points),
            "premium": str(user.premium),
        }
        return response
    else:
        return {
            "user_id": str(user.user_id),
            "email": user.email,
            "token": "No Access Token Found",
            "token_expiration": "none",
            "points": str(user.points),
            "premium": str(user.premium),
        }
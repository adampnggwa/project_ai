from typing import Optional
from database.model import accesstoken
# iki jenge ora user response neng access_token response cok

def user_response(user):
    response = {
        "token": str(user.token),
        "token_expiration": str(user.token_expiration),
        "points": str(user.points),
    }
    return response

# iki anyar lagi tak gawe 
async def access_token_response(user_id):
    data = await accesstoken.filter(user_id=user_id).first()
    return{
        'token': str(data.token),
        'exp': str(data.token_expiration)
    }

def pesan_response(message: str, email: Optional[str]='anonymus'):
    return{
        'email': email,
        'message': message
    }

def response_user(user):
    response = {
        "user_id": str(user.user_id),
        "email": user.email,
        "token": str(user.token),
        "token_expiration": str(user.token_expiration),
        "points": str(user.points),
        "premium": str(user.premium),
    }
    return response
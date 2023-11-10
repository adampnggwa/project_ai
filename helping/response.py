from typing import Optional

def user_response(user):
    response = {
        "user_id": str(user.user_id),
        "email": user.email,
        "token": str(user.token),
        "token_expiration": str(user.token_expiration),
        "points": str(user.points),
    }
    return response

def pesan_response(email: Optional[str], message: str):
    if email is None:
        email = 'anonymus'
    return{
        'email': email,
        'message': message
    }

def premium_response(user):
    response = {
        "email": user.email,
        "message": 'congratulations, now you have a premium subscription',
        "premium_expiration": str(user.premium_expiration),
    }
    return response
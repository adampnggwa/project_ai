from typing import Optional

def user_response(user):
    response = {
        "user_id": str(user.user_id),
        "email": user.email,
        "token": str(user.token),
        "token_expiration": str(user.token_expiration),
    }
    return response

def pesan_response(email: Optional[str], pesan: str):
    if email is None:
        email = 'anonymus'
    return{
        'email': email,
        'pesan': pesan
    }
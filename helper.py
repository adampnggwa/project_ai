import secrets
import pytz
from datetime import datetime, timedelta

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

def user_response(user):
    response = {
        "user_id": str(user.user_id),
        "email": user.email,
        "token": str(user.token),
        "token_expiration": str(user.token_expiration), 
        "refresh_token": str(user.refresh_token),
    }
    return response

async def create_token(user):
    token = secrets.token_hex(16)
    token_expiration = datetime.now(pytz.utc) + timedelta(hours=1)
    user.token = token
    user.token_expiration = token_expiration  
    await user.save()
    
async def check_token_expired(user):
    current_time = datetime.now(pytz.utc)
    if user.token_expiration <= current_time:  
        user.token = None
        await user.save()
        return True
    return False

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
    }
    return response

async def create_token(user):
    token = secrets.token_hex(16)
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    current_time = datetime.now(jakarta_tz)
    token_expiration = current_time + timedelta(hours=8)   
    user.token = token
    user.token_expiration = token_expiration
    await user.save()
    
async def check_token_expired(user):
    current_time = datetime.now(pytz.utc)
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    current_time = current_time.astimezone(jakarta_tz)    
    if user.token_expiration <= current_time:
        user.token = None
        await user.save()
        return True
    return False

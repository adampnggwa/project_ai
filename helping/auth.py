import secrets
import pytz
import hashlib
from datetime import datetime, timedelta
from database.model import User

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

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

async def set_verification_token_expiration(user):
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    current_time = datetime.now(jakarta_tz)
    token_expiration = current_time + timedelta(hours=1) 
    user.verification_token_expiration = token_expiration
    await user.save()

async def is_verification_token_expired(user):
    if user.verification_token_expiration is None:
        return True  
    current_time = datetime.now(pytz.utc)
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    current_time = current_time.astimezone(jakarta_tz)
    if user.verification_token_expiration <= current_time:
        return True  
    return False

def hash_password(password: str, salt: str):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()

async def is_token_valid(token: str) -> bool:
    user = await User.get_or_none(token=token)
    if user:
        if await check_token_expired(user):
            return False
        return True
    return False
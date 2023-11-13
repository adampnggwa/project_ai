import secrets
import pytz
import hashlib
from datetime import datetime, timedelta
from database.model import User

def hash_password(password: str, salt: str):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()

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
    current_time = datetime.now(pytz.utc)
    token_expiration = current_time + timedelta(hours=8)
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

async def is_token_valid(token: str) -> bool:
    user = await User.get_or_none(token=token)
    if user:
        if await check_token_expired(user):
            return False
        return True
    return False

async def set_verification_token_expiration(user):
    current_time = datetime.now(pytz.utc)    
    token_expiration = current_time + timedelta(minutes=5) 
    user.verification_token_expiration = token_expiration
    await user.save()

async def is_verification_token_expired(user):
    if user.verification_token_expiration is None:
        return True  
    current_time = datetime.now(pytz.utc)
    if user.verification_token_expiration <= current_time:
        return True  
    return False

async def refreshed_verification(user):
    user.verification_token_refreshed = True
    await user.save() 

async def user_verification_token(user, meta):
    if user.verification_token and user.verification_token == meta.verification_token:
        user.verification_token = None
        user.verification_token_expiration = None 
        user.verified = True
        await user.save()
        return True
    else:
        return False

async def set_premium_expiration(user):
    current_time = datetime.now(pytz.utc)
    premium_expiration = current_time + timedelta(days=30)
    user.premium_expiration = premium_expiration
    user.premium = True
    await user.save()

async def cek_premium_expired(user):  
    current_time = datetime.now(pytz.utc)
    if user.premium_expiration <= current_time:
        user.premium = False
        user.premium_expiration = None
        await user.save()
        return False  
    else:
        return True
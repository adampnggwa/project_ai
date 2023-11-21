import secrets
import pytz
import hashlib
from datetime import datetime, timedelta
from database.model import User, accesstoken

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

async def create_token(user_id: int):
    token = secrets.token_hex(16)
    current_time = datetime.now(pytz.utc)
    token_expiration = current_time + timedelta(hours=8)
    save = accesstoken(user_id=user_id, token=token, token_expiration=token_expiration)
    access_token_data = await accesstoken.filter(user_id=user_id).first()
    if access_token_data:
        check = await check_token_expired(user_id=user_id)
        if check is True:
            await save.save()
            return True
        else:
            access_token_data.token_expiration = token_expiration
            access_token_data.save()
            return True
    else:
        await save.save()
        return True

async def check_token_expired(user_id: int):
    current_time = datetime.now(pytz.utc)
    data_access_token = await accesstoken.filter(user_id=user_id).first()
    if data_access_token:
        if data_access_token.token_expiration <= current_time:
            # case token sudah basi
            data_access_token.token = None
            await data_access_token.save()
            return True
        else:
            # case token belum basi
            return False
    else:
        # case token tidak ditemukan
        return True

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
    user.points = 120
    user.premium = True
    await user.save()

async def cek_premium_expired(user):  
    current_time = datetime.now(pytz.utc)
    if user.premium_expiration <= current_time:
        user.premium = False
        user.premium_expiration = None
        user.points = 50
        await user.save()
        return False  
    else:
        return True
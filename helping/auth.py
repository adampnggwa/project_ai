import secrets
import pytz
import hashlib
import re
import bcrypt
from datetime import datetime, timedelta
from database.model import userdata, accesstoken
from typing import Optional

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

def cek_valid_email(email: str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

async def apakahAccessTokenValid(access_token):
    current_time = datetime.now(pytz.utc)
    data_access_token = await accesstoken.filter(token=access_token).first()
    if data_access_token: # cek data token milik user id ini ada atau tidak
        if data_access_token.token_expiration <= current_time:
            # case token sudah basi
            await data_access_token.delete()
            return{
                'status': False,
                'keterangan': 'token sudah exp login meneh oy'
            }
        else:
            # case token belum basi
            return{
                'status': True,
                'keterangan': data_access_token.user_id
            }
    else:
        # case token tidak ditemukan
        return {
            'status': False,
            'keterangan': 'token anda tidak ditemukan login kono cok'
        }

async def cek_dulu_gaksih_token_verifikationnya(token, email):
    current_time = datetime.now(pytz.utc)
    user = await userdata.filter(email=email).first()
    if user.verification_token == token:
        if user.verification_token_expiration >= current_time:
            return{
                'status': True,
                'keterangan': user.user_id
            }
        else:
            return{
                'status': False,
                'keterangan': 'anjay basi'
            }
    else:
        return{
            'status': False,
            'keterangan': 'anjay salah'
        }
            
def create_token_verivication():
    current_time = datetime.now(pytz.utc)    
    token_expiration = current_time + timedelta(minutes=5) 
    verification_token = secrets.token_hex(16)
    return{
        'konten': verification_token,
        'exp': token_expiration 
    }

def enx_password(password: str):
    salt = bcrypt.gensalt()
    bytes = password.encode('utf-8')
    hash = bcrypt.hashpw(bytes, salt)
    return hash

def cek_password(password_input, password_database):
    bytes = password_input.encode('utf-8')
    password_data = password_database
    result = bcrypt.checkpw(bytes, password_data)
    return result
    
async def create_access_token(user):
    current_time = datetime.now(pytz.utc)    
    token = secrets.token_hex(16)
    data = await accesstoken.filter(user_id=user.user_id).first()
    if data:
        if data.token_expiration <= current_time:
            data.token_expiration = current_time
            await data.save()
        else:
            data.delete()
            data_baru = accesstoken(user_id = user.user_id, token=token, token_expiration= current_time)
            await data_baru.save()
    else:
        data_baru = accesstoken(user_id = user.user_id, token=token, token_expiration= current_time)
        await data_baru.save()
        
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
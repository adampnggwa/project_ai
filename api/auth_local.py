from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import secrets
from database.model import User
from body.auth import signupORsignin
from helping.response import user_response, pesan_response
from helping.auth import credentials_to_dict, create_token, check_token_expired, hash_password

router = APIRouter(prefix='/auth-local', tags=['auth-local'])

@router.post('/signup')
async def signup(meta: signupORsignin):
    user_exists = await User.exists(email=meta.email)
    if user_exists:
        response = pesan_response(email=meta.email, pesan='email ini sudah mendaftar')
        return JSONResponse (response, status_code=403)
    salt = secrets.token_hex(16)
    hashed_password = hash_password(meta.password, salt)
    await User.create(email=meta.email, password=hashed_password + salt)
    response = pesan_response(email=meta.email, pesan='email berhasil didaftarkan')
    return JSONResponse (response, status_code=201)

@router.post('/signin')
async def signin(meta: signupORsignin):
    user = await User.get(email=meta.email)
    if user is None:
        response = pesan_response(email=meta.email, pesan='email anda masih belum terdaftar')
        return JSONResponse (response, status_code=403)
    salt = user.password[-32:]
    hashed_input_password = hash_password(meta.password, salt)
    if user.password[:-32] != hashed_input_password:
        response = pesan_response(pesan='email atau password anda tidak valid')
        return JSONResponse(response, status_code=401)
    await create_token(user)
    response = user_response(user=user)
    return JSONResponse (response, status_code=200)
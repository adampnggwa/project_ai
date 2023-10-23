from fastapi import APIRouter, HTTPException
from email_validator import validate_email, EmailNotValidError
from helping.response import user_response, pesan_response
from helping.auth import create_token, hash_password
from fastapi.responses import JSONResponse
from helping.confirm import send_confirm
from body.auth import signupORsignin
from database.model import User
import secrets

router = APIRouter(prefix='/auth-local', tags=['auth-local'])

@router.post('/signup')
async def signup(meta: signupORsignin):
    user_exists = await User.exists(email=meta.email)
    if user_exists:
        raise HTTPException(status_code=403, detail="This email is already registered")
    try:
        valid = validate_email(meta.email)
        email = valid["email"]
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail="Invalid email format")
    verification_token = secrets.token_hex(16) # Generate unique verification token
    salt = secrets.token_hex(16)
    hashed_password = hash_password(meta.password, salt)
    await User.create(email=email, password=hashed_password + salt, verification_token=verification_token) # Create user with verification token
    send_confirm(email, verification_token) # Send verification email
    response = pesan_response(email=email, message='Email successfully registered. Please check your email for verification.')
    return JSONResponse(response, status_code=201)

@router.get('/confirm_email')
async def confirm_email(verification_token: str):
    user = await User.filter(verification_token=verification_token).first() # Temukan pengguna dengan token verifikasi yang sesuai
    if user is None:
        raise HTTPException(status_code=404, detail="Verification token not found")
    user.verification_token = None # Hapus token verifikasi
    user.verified = True # Setel pengguna sebagai diverifikasi
    await user.save()
    response = pesan_response(email=user.email, message='Email confirmed successfully')
    return JSONResponse(response, status_code=200)

@router.post('/signin')
async def signin(meta: signupORsignin):
    user = await User.get_or_none(email=meta.email)
    if user is None:
        raise HTTPException(status_code=403, detail="Your email is not yet registered")
    else:
        salt = user.password[-32:]
        hashed_input_password = hash_password(meta.password, salt)
        if user.password[:-32] != hashed_input_password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        await create_token(user)
        response = user_response(user)
        return JSONResponse(response, status_code=200)
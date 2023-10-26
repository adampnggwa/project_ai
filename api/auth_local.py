from fastapi import APIRouter, HTTPException
from email_validator import validate_email, EmailNotValidError
from helping.response import user_response, pesan_response
from helping.auth import create_token, hash_password, is_verification_token_expired, set_verification_token_expiration
from fastapi.responses import JSONResponse
from helping.confirm import send_confirm
from body.auth import signupORsignin, VerifyRegistration
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
    verification_token = secrets.token_hex(16) 
    salt = secrets.token_hex(16)
    hashed_password = hash_password(meta.password, salt)
    user = await User.create(email=email, password=hashed_password + salt, verification_token=verification_token) 
    await set_verification_token_expiration(user)
    verification_token_expiration = user.verification_token_expiration
    send_confirm(email, verification_token, verification_token_expiration) 
    response = pesan_response(email=email, message='Email successfully registered. Please check your email for verification.')
    return JSONResponse(response, status_code=201)

@router.post('/verify-registration')
async def verify_registration(meta: VerifyRegistration):
    user = await User.get_or_none(email=meta.email)
    if user is None:
        raise HTTPException(status_code=403, detail="Your email is not yet registered")
    if await is_verification_token_expired(user):
        raise HTTPException(status_code=401, detail="Verification token has expired")
    if user.verification_token and user.verification_token == meta.verification_token:
        user.verification_token = None
        user.verification_token_expiration = None 
        user.verified = True
        await user.save()        
        response = pesan_response(email=meta.email, message="Congratulations, you have been verified, then you can signin.")
        return JSONResponse(response, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid verification token")

@router.post('/signin')
async def signin(meta: signupORsignin):
    user = await User.get_or_none(email=meta.email)
    if user is None:
        raise HTTPException(status_code=403, detail="Your email is not yet registered")
    else:
        if not user.verified:
            raise HTTPException(status_code=403, detail="User is not verified. Please complete the verification process.")        
        salt = user.password[-32:]
        hashed_input_password = hash_password(meta.password, salt)
        if user.password[:-32] != hashed_input_password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        await create_token(user)
        response = user_response(user)
        return JSONResponse(response, status_code=200)
from fastapi import APIRouter, HTTPException
from email_validator import validate_email, EmailNotValidError
from helping.response import user_response, pesan_response
from helping.auth import create_token, hash_password, is_verification_token_expired, set_verification_token_expiration, user_verification_token, refreshed_verification
from fastapi.responses import JSONResponse
from helping.confirm import send_confirm
from body.auth import signupORsignin, VerifyRegistration, RefreshVerificationToken
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
    if await user_verification_token(user, meta):
        response = pesan_response(email=meta.email, message="Congratulations, you have been verified, then you can signin.")
        return JSONResponse(response, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid verification token")

@router.post('/refresh-verification-token')
async def refresh_verification_token(meta: RefreshVerificationToken):
    user = await User.get_or_none(email=meta.email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not await is_verification_token_expired(user):
        raise HTTPException(status_code=400, detail="Verification token is not expired")
    if user.verification_token_refreshed:
        raise HTTPException(status_code=400, detail="Verification token can only be refreshed once")
    new_verification_token = secrets.token_hex(16)
    user.verification_token = new_verification_token
    await set_verification_token_expiration(user)
    verification_token_expiration = user.verification_token_expiration
    await refreshed_verification(user)
    send_confirm(user.email, new_verification_token, verification_token_expiration)
    response = pesan_response(email=meta.email, message="Verification token refreshed. Check your email for the new token.")
    return JSONResponse(response, status_code=200)

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
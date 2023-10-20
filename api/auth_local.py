from fastapi import APIRouter, HTTPException
from email_validator import validate_email, EmailNotValidError
from helping.response import user_response, pesan_response
from helping.auth import create_token, hash_password
from fastapi.responses import JSONResponse
from body.auth import signupORsignin
from database.model import User
from typing import Optional
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
    salt = secrets.token_hex(16)
    hashed_password = hash_password(meta.password, salt)
    await User.create(email=email, password=hashed_password + salt)
    response = pesan_response(email=email, message='Email successfully registered')
    return JSONResponse(response, status_code=201)

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
    
@router.put('/edit-profile')
async def edit_profile(email: str, current_password: str, new_email: Optional[str] = None, new_password: Optional[str] = None):
    user = await User.get_or_none(email=email)
    if user is None:
        raise HTTPException(status_code=403, detail="Your email is not registered")
    salt = user.password[-32:]
    hashed_input_password = hash_password(current_password, salt)
    if user.password[:-32] != hashed_input_password:
        raise HTTPException(status_code=401, detail="Invalid password")
    if new_email:
        if new_email != user.email:
            email_exists = await User.exists(email=new_email)
            if email_exists:
                raise HTTPException(status_code=403, detail="Email already in use")
        try:
            valid = validate_email(new_email)
            email = valid["email"]
        except EmailNotValidError as e:
            raise HTTPException(status_code=400, detail="Invalid email format")
        user.email = email
    if new_password:
        salt = secrets.token_hex(16)
        hashed_password = hash_password(new_password, salt)
        user.password = hashed_password + salt
    await user.save()
    response = pesan_response(email=user.email, message='Profile updated successfully')
    return JSONResponse(response, status_code=200)
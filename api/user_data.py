from fastapi import APIRouter, HTTPException, Header
from email_validator import validate_email, EmailNotValidError
from helping.response import user_response, pesan_response
from fastapi.responses import JSONResponse
from helping.auth import is_token_valid, hash_password
from database.model import User
from typing import Optional
import secrets

router = APIRouter(prefix='/user-data', tags=['user-data'])

@router.put('/update-profile')
async def edit_profile(
    email: str,
    password: str,
    new_email: Optional[str] = None,
    new_password: Optional[str] = None,
    token: str = Header(...),
):
    validasi = await is_token_valid(token=token)
    if not validasi:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await User.get_or_none(email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    salt = user.password[-32:]
    hashed_input_password = hash_password(password, salt)
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

@router.get('/get-profile')
async def get_profile(email: str, token: str = Header(...)):
    validasi = await is_token_valid(token=token)
    if not validasi:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await User.get_or_none(email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_info = user_response(user)
    return JSONResponse(user_info, status_code=200)

@router.delete('/delete-account')
async def delete_account(email: str, password: str, token: str = Header(...)):
    validasi = await is_token_valid(token=token)
    if not validasi:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await User.get_or_none(email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    salt = user.password[-32:]
    hashed_input_password = hash_password(password, salt)
    if user.password[:-32] != hashed_input_password:
        raise HTTPException(status_code=401, detail="Invalid password")
    await user.delete()
    response = pesan_response(email=user.email, message='Account deleted successfully')
    return JSONResponse(response, status_code=200)
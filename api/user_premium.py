from fastapi import APIRouter, HTTPException, Header
from database.model import User
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from helping.response import premium_response
from helping.auth import is_token_valid, set_premium_expiration
import pytz

router = APIRouter(prefix='/user-premium', tags=['user-premium'])

@router.post('/set-premium')
async def set_premium(token: str = Header(...)):
    validasi = await is_token_valid(token=token)
    if validasi is False:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await User.get(token=token)
    if user.premium:
        raise HTTPException(status_code=400, detail="You are already subscribed to premium.")
    await set_premium_expiration(user)
    response = premium_response(user)
    return JSONResponse(response, status_code=200)
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from helping.response import pesan_response
from helping.auth import set_premium_expiration, apakahAccessTokenValid
from database.model import userdata
router = APIRouter(prefix='/user-premium', tags=['user-premium'])

@router.post('/set-premium')
async def set_premium(access_token: str = Header(...)):
    validasi = await apakahAccessTokenValid(access_token=access_token)
    if validasi['status'] is False:
        raise HTTPException(status_code=401, detail=validasi['keterangan'])
    else:
        user_id = validasi["keterangan"]
    
    user = await userdata.filter(user_id=user_id).first()
   
    if user.premium:
        raise HTTPException(status_code=400, detail="You are already subscribed to premium.")
    
    await set_premium_expiration(user)
    response = pesan_response(message='kowe wes ddddvcfhjgasdvfhjg premium', email=user.email)
    
    return JSONResponse(response, status_code=200)
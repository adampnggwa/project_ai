from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from helping.response import pesan_response
from helping.auth import set_premium_expiration, apakahAccessTokenValid
from database.model import userdata, buyerdata
from body.user_payment import BuyerDataRequest

router = APIRouter(prefix='/user-premium', tags=['user-premium'])

@router.post('/premium-account')
async def premium_account(access_token: str = Header(...)):
    validasi = await apakahAccessTokenValid(access_token=access_token)
    if validasi['status'] is False:
        raise HTTPException(status_code=401, detail=validasi['keterangan'])
    else:
        user_id = validasi["keterangan"]
    user = await userdata.filter(user_id=user_id).first()
    if user.premium:
        raise HTTPException(status_code=400, detail="You are already subscribed to premium.")
    await set_premium_expiration(user)
    response = pesan_response(message='Congratulations, you have subscribed to premium', email=user.email)
    return JSONResponse(response, status_code=201)

@router.post('/buyer-data')
async def buyer_data(meta: BuyerDataRequest, access_token: str = Header(...)):
    validasi = await apakahAccessTokenValid(access_token=access_token)
    if validasi['status'] is False:
        raise HTTPException(status_code=401, detail=validasi['keterangan'])
    else:
        user_id = validasi["keterangan"]
    user = await userdata.filter(user_id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    buyer = buyerdata(
        user_id=user_id,
        first_name=meta.first_name,
        last_name=meta.last_name,
        address_line=meta.address_line,
        city=meta.city,
        region=meta.region,
        postcode=meta.postcode,
        country=meta.country,
    )
    await buyer.save()
    response = pesan_response(email=user.email, message='Buyer data added successfully')
    return JSONResponse(response, status_code=201)
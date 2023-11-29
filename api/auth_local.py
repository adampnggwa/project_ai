from fastapi import APIRouter, HTTPException
from helping.response import pesan_response, access_token_response
from helping.auth import enx_password, create_verification_token, cek_verification_token, create_access_token, cek_valid_email, cek_password
from fastapi.responses import JSONResponse
from helping.confirm import send_confirm
from body.auth import signupORsignin, VerifyRegistration
from database.model import userdata
from datetime import datetime
import pytz 

router = APIRouter(prefix='/auth-local', tags=['auth-local'])
    
@router.post('/signup')
async def signup(meta: signupORsignin):
    user = await userdata.filter(email=meta.email).first()
    value = create_verification_token()
    hashed_password = enx_password(meta.password)
    response = pesan_response(email=meta.email, message='Email successfully registered. Please check your email for verification')
    email_ceker = cek_valid_email(email=meta.email)
    if email_ceker is False:
        raise HTTPException(detail='Invalid email format', status_code=500)
    if user:
        if user.verified is True:
            raise HTTPException(detail='This email is already registered', status_code=403)
        else:
            send_confirm(email=meta.email, verification_token=value['konten'], verification_token_expiration=value['exp'])
            if user.google_auth is True:
                user.email = meta.email
                user.password = hashed_password
                user.verification_token = value['konten']
                user.verification_token_expiration = value['exp']
            else:
                user.email = meta.email
                user.password = hashed_password
                user.verification_token = value['konten']
                user.verification_token_expiration = value['exp']
            await user.save()
            return JSONResponse(response, status_code=200)
    else:
        send_confirm(email=meta.email, verification_token=value['konten'], verification_token_expiration=value['exp'])
        await userdata.create(email=meta.email, password=hashed_password, verification_token=value['konten'], verification_token_expiration= value['exp'])
        return JSONResponse(response, status_code=200)
    
@router.post('/verification-account')
async def verification(meta: VerifyRegistration):
    user = await userdata.filter(email=meta.email).first()
    if user:
        check_verifikasi = await cek_verification_token(email=meta.email)
        if check_verifikasi['status'] is False:
            raise HTTPException(detail=check_verifikasi['keterangan'], status_code=500)
        else:
            user.verification_token = None
            user.verification_token_expiration = None
            user.verified = True
            user.points = 50
            await user.save()
            repsonse = pesan_response(email=meta.email, message='Congratulations, you have been verified, then you can signin')
            return JSONResponse(repsonse, status_code=200)
    else:
        raise HTTPException(detail='Your email is not yet registered', status_code=500)

@router.post('/signin')
async def signin(meta:signupORsignin):
    user = await userdata.filter(email=meta.email).first()
    email_ceker = cek_valid_email(email=meta.email)
    if email_ceker is False:
        raise HTTPException(detail='Invalid email format', status_code=500)
    if user:
        if user.verified is False:
            raise HTTPException(detail='User is not verified. Please complete the verification process', status_code=500)
        else:
            if cek_password(password_database=user.password, password_input=meta.password) is True:
                user.last_login = datetime.now(pytz.utc).date()
                await user.save()
                await create_access_token(user=user)
                response = await access_token_response(user_id=user.user_id)
                return JSONResponse(response, status_code=200)
            else:
                raise HTTPException(detail='Invalid email or password', status_code=500)
    else:
        raise HTTPException(detail='Your email is not yet registered', status_code=500)
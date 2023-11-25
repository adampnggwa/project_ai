from fastapi import APIRouter, HTTPException
import json
from helping.response import pesan_response, access_token_response
from helping.auth import enx_password, create_token_verivication, cek_dulu_gaksih_token_verifikationnya, create_access_token, cek_valid_email, cek_password
from fastapi.responses import JSONResponse
from helping.confirm import send_confirm
from body.auth import signupORsignin, VerifyRegistration
from database.model import userdata

router = APIRouter(prefix='/auth-local', tags=['auth-local'])
    
@router.post('/register')
async def register(meta: signupORsignin):
    user = await userdata.filter(email=meta.email).first()
    value = create_token_verivication()
    hashed_password = enx_password(meta.password)
    response = pesan_response(email=meta.email, message='tilik email ya adik adik')
    
    email_ceker = cek_valid_email(email=meta.email)
    if email_ceker is False:
        raise HTTPException(detail='ngelebokke opo kowe ki', status_code=500)
    
    if user:

        if user.verified is True:
            raise HTTPException(detail='raoleh daftar meneh ', status_code=403)
        else:
            send_confirm(email=meta.email, token=value['konten'], exp=value['exp'])
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
        send_confirm(email=meta.email, token=value['konten'], exp=value['exp'])
        await userdata.create(email=meta.email, password=hashed_password, verification_token=value['konten'], verification_token_expiration= value['exp'])
        return JSONResponse(response, status_code=200)
    
@router.post('/centang-biru-dulu-gak-sih')
async def verifed(meta: VerifyRegistration):
    user = await userdata.filter(email=meta.email).first()
    if user:
        check_verifikasi = await cek_dulu_gaksih_token_verifikationnya(email=meta.email, token=meta.token_konfirmasi)
        if check_verifikasi['status'] is False:
            raise HTTPException(detail=check_verifikasi['keterangan'], status_code=500)
        else:
            user.verification_token = None
            user.verification_token_expiration = None
            user.verified = True
            await user.save()
            repsonse = pesan_response(email=meta.email, message='hore udah jadi')
            return JSONResponse(repsonse, status_code=200)
    else:
        raise HTTPException(detail='user tidak ditemukann bjr', status_code=500)

@router.post('/login-coy')
async def login(meta:signupORsignin):
    user = await userdata.filter(email=meta.email).first()
    email_ceker = cek_valid_email(email=meta.email)
    if email_ceker is False:
        raise HTTPException(detail='iki user e dasar ***', status_code=500)
    if user:
        if user.verified is False:
            raise HTTPException(detail='anjay kamu gak centang biru', status_code=500)
        else:
            if cek_password(password_database=user.password, password_input=meta.password) is True:
                await create_access_token(user=user)
                response = await access_token_response(user_id=user.user_id)
                return JSONResponse(response, status_code=200)
            else:
                raise HTTPException(detail='hayo kamu curi akun ya', status_code=500)
    else:
        raise HTTPException(detail='malas isi sendiri detailnya', status_code=500)
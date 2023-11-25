from fastapi import APIRouter, HTTPException, Header
from helping.response import pesan_response, response_user
from fastapi.responses import JSONResponse
from database.model import userdata
from helping.auth import apakahAccessTokenValid, cek_password, cek_valid_email, enx_password
from body.user import EditProfileRequest, DeleteAccountRequest
import secrets

router = APIRouter(prefix='/user-data', tags=['user-data'])

@router.put('/update-profile')
async def update_profile(meta: EditProfileRequest, access_token: str = Header(...)):
    validasi = await apakahAccessTokenValid(access_token=access_token)
    if validasi['status'] is False:
        raise HTTPException(status_code=401, detail=validasi['keterangan'])
    else:
        user_id = validasi["keterangan"]
    
    user = await userdata.filter(user_id=user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if cek_password(password_database=user.password, password_input=meta.password) is False:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    if meta.new_email:
        
        if meta.new_email != user.email:
            email_exists = await userdata.exists(email=meta.new_email)
            
            if email_exists:
                raise HTTPException(status_code=403, detail="Email already in use")
            
            if cek_valid_email(email=meta.new_email) is False:
                raise HTTPException(status_code=403, detail='user e tolol diomongi ngeyel')
            
            user.email = meta.new_email
    
    if meta.new_password:
        password = enx_password(password=meta.new_password)
        user.password = password
        
    await user.save()
    
    response = pesan_response(email=user.email, message='Profile updated successfully')
    
    return JSONResponse(response, status_code=201)

@router.get('/get-profile')
async def get_profile(access_token: str = Header(...)):
    validasi = await apakahAccessTokenValid(access_token=access_token)
    if validasi['status'] is False:
        raise HTTPException(status_code=401, detail=validasi['keterangan'])
    else:
        user_id = validasi["keterangan"]
    
    user = await userdata.filter(user_id=user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return JSONResponse(content=response_user(user=user), status_code=200)

@router.delete('/delete-account')
async def delete_account(meta: DeleteAccountRequest, access_token: str = Header(...)):
    
    validasi = await apakahAccessTokenValid(access_token=access_token)
    if validasi['status'] is False:
        raise HTTPException(status_code=401, detail=validasi['keterangan'])
    else:
        user_id = validasi["keterangan"]
    
    user = await userdata.filter(user_id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    if cek_password(password_database=user.password, password_input=meta.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    await user.delete()
    
    response = pesan_response(email=user.email, message='Account deleted successfully')
    
    return JSONResponse(response, status_code=204)
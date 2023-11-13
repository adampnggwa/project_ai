from fastapi import APIRouter, HTTPException, UploadFile, Header
from database.model import User, GeneratedImage, EditedImage, GeneratedVariation
from helping.action import generate_variation, generate_image, edit_image
from fastapi.responses import JSONResponse
from datetime import datetime
from helping.limit import can_use_action, reset_user_points
from helping.auth import is_token_valid, cek_premium_expired
from body.action import ImageRequest
from PIL import Image
import tempfile
import shutil
import pytz
import os

router = APIRouter(prefix='/action-utama', tags=['ACTION'])

@router.post('/generate-image')
async def generate(meta: ImageRequest, token: str= Header(...)):
    validasi = await is_token_valid(token=token)
    if validasi is False:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await User.get(token=token)
    if reset_user_points(user) or can_use_action(user, 'generate-image', meta.size):
        if meta.size == 'small':
            size = '256x256'
        elif meta.size == 'medium':
            size = '512x512'
        elif meta.size == 'large':
            size = '1024x1024'
        else:
            raise HTTPException(status_code=400, detail="Entered the wrong value in the size parameter")
        prompt = meta.prompt
        response_data = generate_image(prompt, size)
        response_data["size"] = f"{meta.size} ({size})"
        combined_size = f"{meta.size} ({size})"
        now_local = datetime.now(pytz.timezone('Asia/Jakarta'))
        generated_image = await GeneratedImage.create(user=user, image_url=response_data["image_url"], prompt=prompt, size=combined_size)
        generated_image.created_at = now_local
        await generated_image.save()
        await user.save()
        return JSONResponse(content=response_data, status_code=201)
    else:
        raise HTTPException(status_code=400, detail="Insufficient points. Please wait 8 hours to reset the points.")
    
@router.post('/edit-image')
async def edit(prompt: str, image: UploadFile, mask: UploadFile = None, token: str = Header(...)):
    size: str = "1024x1024"
    validasi = await is_token_valid(token=token)
    if validasi is False:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await User.get(token=token) 
    if user.premium is True:
        valid_prem = await cek_premium_expired(user)  
        if valid_prem is False:
           raise HTTPException(status_code=400, detail="Premium subscription has expired. You must subscribe again to use Edit Image.")  
        elif valid_prem is True:
            if reset_user_points(user) or can_use_action(user, 'edit-image'): 
                image_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                mask_temp = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as image_temp:
                        shutil.copyfileobj(image.file, image_temp)
                    if mask:
                        mask_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                        shutil.copyfileobj(mask.file, mask_temp)
                        with Image.open(mask_temp.name) as mask_pil:
                            mask_pil = mask_pil.convert("L")
                            mask_pil = mask_pil.resize((1024, 1024))
                            mask_pil.save(mask_temp.name, format="PNG")
                    response_data = edit_image(prompt, image_temp, mask_temp, size)
                    now_local = datetime.now(pytz.timezone('Asia/Jakarta'))
                    edited_images = await EditedImage.create(user=user, image_url=response_data["image_url"], prompt=prompt)
                    edited_images.created_at = now_local
                    await edited_images.save()
                    await user.save()
                    return JSONResponse(content=response_data, status_code=200)
                finally:
                    os.remove(image_temp.name)
                    if mask_temp:
                        mask_temp.close()
                        os.remove(mask_temp.name)
            else:
                raise HTTPException(status_code=400, detail="Insufficient points. Please wait 8 hours to reset the points.")
    else:  
        raise HTTPException(status_code=400, detail="You need premium subscription to use Edit Image")
    
@router.post('/generate-variation')
async def variation(image: UploadFile, token: str = Header(...)):
    size: str = "1024x1024"
    validasi = await is_token_valid(token=token)
    if validasi is False:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await User.get(token=token)
    if user.premium is True:
        valid_prem = await cek_premium_expired(user)  
        if valid_prem is False:
           raise HTTPException(status_code=400, detail="Premium subscription has expired. You must subscribe again to use Generate Variation.")  
        elif valid_prem is True:
            if reset_user_points(user) or can_use_action(user, 'generate-variation'):    
                image_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as image_temp:
                        shutil.copyfileobj(image.file, image_temp)
                    response_data = generate_variation(image_temp, size)
                    now_local = datetime.now(pytz.timezone('Asia/Jakarta'))
                    generated_variations = await GeneratedVariation.create(user=user, image_url=response_data["image_url"])
                    generated_variations.created_at = now_local
                    await generated_variations.save()
                    await user.save()
                    return JSONResponse(content=response_data, status_code=201)
                finally:
                    os.remove(image_temp.name)
            else:
                raise HTTPException(status_code=400, detail="Insufficient points. Please wait 8 hours to reset the points.")  
    else:  
        raise HTTPException(status_code=400, detail="You need premium subscription to use Generate Variation") 
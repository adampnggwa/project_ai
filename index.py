from fastapi import FastAPI, Request, HTTPException, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
from body import ImageRequest
from fastapi.middleware.cors import CORSMiddleware
from tortoise.exceptions import IntegrityError
from database import init_db
from configs import config
from model import User, GeneratedImage
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO
from helper import (
    credentials_to_dict, 
    user_response, 
    create_token, 
    check_token_expired, 
)

import google_auth_oauthlib.flow
import os
import openai
import requests
import secrets
import hashlib
import pytz
import tempfile
import shutil

app = FastAPI()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

@app.on_event("startup")
async def startup_event():
    init_db(app)

origins = [
    "http://localhost:3000/",
    "http://localhost:3000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()

def generate_image(prompt, size="1024x1024"):
    openai.api_key = config.api_key_openai
    response = openai.Image.create(prompt=prompt, n=1, size=size)
    image_url = response['data'][0]['url']
    response_data = {
        "status": "success",
        "code": 201,
        "message": "image created successfully",
        "image_url": image_url
    }
    return response_data

def edit_image(token, prompt, image_temp, mask_temp, size="1024x1024"):
    with Image.open(image_temp.name) as image_pil:
        if mask_temp:
            with Image.open(mask_temp.name) as mask_pil:
                if image_pil.size != mask_pil.size:
                    raise HTTPException(status_code=400, detail="Image and mask dimensions must match")
        openai.api_key = config.api_key_openai
        if mask_temp:
            response = openai.Image.create_edit(
                image=open(image_temp.name, "rb"),
                mask=open(mask_temp.name, "rb"),
                prompt=prompt,
                n=1,
                size=size
            )
        else:
            response = openai.Image.create(prompt=prompt, n=1, size=size)
        image_url = response['data'][0]['url']
        response_data = {
            "status": "success",
            "code": 201,
            "message": "image edited successfully",
            "image_url": image_url
        }
        return response_data

def generate_variation(token, image_temp, size="1024x1024"):
    try:
        with Image.open(image_temp.name) as image_pil:
            byte_stream = BytesIO()
            image_pil.save(byte_stream, format='PNG')
            byte_array = byte_stream.getvalue()
        openai.api_key = config.api_key_openai
        response = openai.Image.create_variation(
            image=byte_array,
            n=1,
            size=size
        )
        image_url = response['data'][0]['url']
        response_data = {
            "status": "success",
            "code": 201,
            "message": "image variation created successfully",
            "image_url": image_url
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def increment_image_count(token: str):
    try:
        user = await User.get(token=token)
        user.image_count += 1  
        await user.save()
    except User.DoesNotExist:
        pass

async def is_token_valid(token: str) -> bool:
    user = await User.get_or_none(token=token)
    if user:
        if await check_token_expired(user):
            raise HTTPException(status_code=401, detail="Token has expired")
        return True
    raise HTTPException(status_code=401, detail="Invalid token")

async def perform_signup(email: str, create_password: str) -> dict:
    try:
        user_exists = await User.exists(email=email)
        if user_exists:
            return {"status": "error", "code": 400, "message": "Email already exists"}
        salt = secrets.token_hex(16)
        hashed_password = hash_password(create_password, salt)
        await User.create(email=email, password=hashed_password + salt)
        return {"status": "success", "code": 201, "message": "User created successfully"}
    except IntegrityError as e:
        return {"status": "error", "code": 400, "message": "Error creating user: Email already exists"}
    except Exception as e:
        return {"status": "error", "code": 500, "message": "Error creating user: Internal Server Error"}

async def perform_signin(email: str, password: str) -> dict:
    try:
        user = await User.get(email=email)
    except User.DoesNotExist:
        return {"status": "error", "code": 404, "message": "User not found"}
    salt = user.password[-32:]
    hashed_input_password = hash_password(password, salt)
    if user.password[:-32] != hashed_input_password:
        return {"status": "error", "code": 400, "message": "Invalid email or password"}
    await create_token(user)
    response = {
        "status": "success",
        "code": 200,
        "message": "login successfully",
        "user_id": user.user_id,
        "token": user.token,
        "token_expiration": user.token_expiration
    }
    return response

@app.post("/signup/")
async def signup(email: str, create_password: str):
    response = await perform_signup(email, create_password)
    return response

@app.post("/signin/")
async def signin(email: str, password: str):
    response = await perform_signin(email, password)
    return response

@app.get("/register")
async def regist():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['email', 'profile']  
    )
    flow.redirect_uri = config.redirect_uri_register
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@app.get("/login")
async def login():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['email', 'profile']  
    )
    flow.redirect_uri = config.redirect_uri_login
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@app.get("/auth2callbackRegister")
async def auth2callback_register(request: Request, state: str):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['email', 'profile'],  
        state=state
    )
    flow.redirect_uri = config.redirect_uri_register
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    access_token = credentials.token

    userinfo_endpoint = 'https://www.googleapis.com/oauth2/v3/userinfo'
    user_info_response = requests.get(userinfo_endpoint, headers={'Authorization': f'Bearer {access_token}'})
    user_info = user_info_response.json()
    email = user_info.get("email")
    nama = user_info.get("name")

    existing_user = await User.filter(email=email).first()
    if not existing_user:
        save = User(nama=nama, email=email)
        await save.save()
        user = await User.filter(email=email).first()
        await create_token(user)
        response = user_response(user)
        return JSONResponse(response, status_code=201)
    else:
        raise HTTPException(status_code=400, detail="Invalid")
    
@app.get("/auth2callbackLogin")
async def auth2callback(request: Request, state: str):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['email', 'profile'],  
        state=state
    )
    flow.redirect_uri = config.redirect_uri_login
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    creds = credentials_to_dict(credentials)
    access_token = credentials.token

    userinfo_endpoint = 'https://www.googleapis.com/oauth2/v3/userinfo'
    user_info_response = requests.get(userinfo_endpoint, headers={'Authorization': f'Bearer {access_token}'})
    user_info = user_info_response.json()
    email = user_info.get("email")

    existing_user = await User.filter(email=email).first()
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid")
    else:
        user = await User.filter(email=email).first()
        await create_token(user)
        response = user_response(user)
        return JSONResponse(response, status_code=200)

@app.post("/generate-image/")
async def generate_image_endpoint(image_request: ImageRequest):
    token = image_request.token
    if not await is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await User.get(token=token)
    now_utc = datetime.now(pytz.utc)
    if (
        user.last_image_generated_at
        and now_utc - user.last_image_generated_at >= timedelta(hours=1)
    ):
        user.image_count = 0
    if user.image_count >= 5:
        raise HTTPException(status_code=400, detail="You have reached the maximum limit of images generated for this hour, please try again after 1 hour")
    prompt = image_request.prompt
    size = image_request.size
    response_data = generate_image(prompt, size)
    now_local = now_utc.astimezone(pytz.timezone('Asia/Jakarta'))
    user.last_image_generated_at = now_local 
    generated_image = await GeneratedImage.create(user=user, image_url=response_data["image_url"], prompt=prompt)
    generated_image.created_at = now_local
    await generated_image.save()
    user.image_count += 1
    await user.save()
    return response_data

@app.post("/edit-image/")
async def edit_image_endpoint(
    token: str,
    prompt: str,
    image: UploadFile,
    mask: UploadFile = None,
    size: str = "1024x1024"
):
    if not await is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
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
        response_data = edit_image(token, prompt, image_temp, mask_temp, size)
        return response_data
    finally:
        os.remove(image_temp.name)
        if mask_temp:
            mask_temp.close()
            os.remove(mask_temp.name)

@app.post("/generate-variation/")
async def generate_variation_endpoint(
    token: str,
    image: UploadFile,
    size: str = "1024x1024"
):
    if not await is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    image_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as image_temp:
            shutil.copyfileobj(image.file, image_temp)
        response_data = generate_variation(token, image_temp, size)
        return response_data
    finally:
        os.remove(image_temp.name)
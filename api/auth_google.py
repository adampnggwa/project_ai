from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from helping.auth import credentials_to_dict, create_access_token
from helping.response import access_token_response
from database.model import userdata
import google_auth_oauthlib.flow
from configs import config
import requests
import os

router = APIRouter(prefix='/google-auth', tags=['GOOGLE-AUTH'])

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

@router.get('/signup')
async def signupGoogle():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials_google.json',
        scopes=['email', 'profile']  
    )
    flow.redirect_uri = config.redirect_uri_register
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@router.get('/signin')
async def signinGoogle():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials_google.json',
        scopes=['email', 'profile']  
    )
    flow.redirect_uri = config.redirect_uri_login
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@router.get('/auth2callbacksignup')
async def callbackSignup(request: Request, state: str):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials_google.json',
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

    existing_user = await userdata.filter(email=email).first()
    if not existing_user:
        save = userdata(email=email, google_auth=True)
        await save.save()
        user = await userdata.filter(email=email).first()
        await create_access_token(user_id=user.user_id)
        response = await access_token_response(user_id=user.user_id)
        return JSONResponse(response, status_code=201)
    else:
        if existing_user.google_auth is True:
            raise HTTPException(status_code=400, detail="Invalid")
        else:
            existing_user.google_auth = True
            existing_user.save()
            await create_access_token(user=existing_user)
            response = await access_token_response(user_id=existing_user.user)
            return JSONResponse(response, status_code=201)

@router.get('/auth2callbacksignin')
async def callbackSignin(request: Request, state: str):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials_google.json',
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

    user = await userdata.filter(email=email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid")
    else:
        if user.google_auth is True:
            user = await userdata.filter(email=email).first()
            await create_access_token(user=user)
            response = await access_token_response(user_id=user.user_id)
            return JSONResponse(response, status_code=200)
        else:
            raise HTTPException(status_code=400, detail="Invalid")
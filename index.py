from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import init_db
from configs import config
import api.action
import api.auth_google
import api.auth_local
import api.user_data
import api.user_premium
import openai

app = FastAPI()
openai.api_key = config.api_key_openai

@app.on_event("startup")
async def startup():
    init_db(app)

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api.action.router)
app.include_router(api.auth_google.router)
app.include_router(api.auth_local.router)
app.include_router(api.user_data.router)
app.include_router(api.user_premium.router)
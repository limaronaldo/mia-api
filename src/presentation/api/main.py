import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config.database import supabase_vault
from src.presentation.api.v1.router import router

for env in supabase_vault.table("decrypted_secrets").select("*").execute().data:
    os.environ[env["name"]] = env["decrypted_secret"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.mbras.com.br",
        "https://mbras.com.br",
        "http://localhost:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router)

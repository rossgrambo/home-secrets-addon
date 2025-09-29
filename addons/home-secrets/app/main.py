import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .secrets_api import router as secrets_router
from .oauth_google import router as google_router

app = FastAPI(title="Home Secrets Server", version="0.1.0")

# CORS
allowed_origins = []
raw = os.getenv("HS_CORS_ALLOWED_ORIGINS", "")
if raw:
    # Only accept concrete origins with scheme://host[:port]
    # If you put a CIDR in config, ignore it here; list concrete web origins you use.
    allowed_origins = [o.strip() for o in raw.split(",") if "://" in o]

# Allow all origins for OAuth endpoints to prevent CORS issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for OAuth functionality
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(secrets_router, prefix="")
app.include_router(google_router, prefix="")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from secrets_api import router as secrets_router
from oauth_google import router as google_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Home Secrets Server", version="0.1.0")

# CORS
allowed_origins = []
raw = os.getenv("HS_CORS_ALLOWED_ORIGINS", "")
if raw:
    # Only accept concrete origins with scheme://host[:port]
    # If you put a CIDR in config, ignore it here; list concrete web origins you use.
    allowed_origins = [o.strip() for o in raw.split(",") if "://" in o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or [],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(secrets_router, prefix="")
app.include_router(google_router, prefix="")

# Log registered routes for debugging
logger.info("Registered routes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        logger.info(f"  {route.methods} {route.path}")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/debug/env")
def debug_env():
    """Debug endpoint to check environment configuration"""
    return {
        "google_enabled": os.getenv("GOOGLE_ENABLED"),
        "google_client_id": "***" if os.getenv("GOOGLE_CLIENT_ID") else None,
        "google_redirect_bases": os.getenv("GOOGLE_REDIRECT_BASES"),
        "hs_api_key": "***" if os.getenv("HS_API_KEY") else None,
        "hs_secret_prefix": os.getenv("HS_SECRET_PREFIX"),
        "all_env_vars": [k for k in os.environ.keys() if k.startswith(("GOOGLE_", "HS_"))]
    }
import os
from fastapi import APIRouter, Header, HTTPException

router = APIRouter()

def require_api_key(x_api_key: str | None):
    expected = os.getenv("HS_API_KEY") or ""
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("/secret/{key}")
def get_secret(key: str, x_api_key: str | None = Header(default=None)):
    require_api_key(x_api_key)

    prefix = os.getenv("HS_SECRET_PREFIX", "HS_")
    env_var = f"{prefix}{key}".upper()
    val = os.getenv(env_var)
    if val is None:
        raise HTTPException(status_code=404, detail=f"{env_var} not set")
    return {"key": key, "env": env_var, "value": val}
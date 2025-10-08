import os
import time
import secrets
import httpx
import logging
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException, Request, Header
from storage import google_get, google_set
from secrets_api import require_api_key

logger = logging.getLogger(__name__)

router = APIRouter()

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"

def _cfg():
    enabled = os.getenv("GOOGLE_ENABLED", "true").lower() == "true"
    cid = os.getenv("GOOGLE_CLIENT_ID", "")
    cs = os.getenv("GOOGLE_CLIENT_SECRET", "")
    scopes = (os.getenv("GOOGLE_SCOPES", "") or "").split()
    label = os.getenv("GOOGLE_TOKEN_LABEL", "default")
    return enabled, cid, cs, scopes, label

def _now() -> int:
    return int(time.time())

@router.get("/oauth/google/start")
def google_start(
    redirect_uri: str,
    x_api_key: str | None = Header(default=None),
    api_key: str | None = None
):
    # Support API key from both header and query parameter
    api_key_to_use = x_api_key or api_key
    require_api_key(api_key_to_use)

    enabled, cid, cs, scopes, label = _cfg()
    if not enabled:
        raise HTTPException(400, "Google OAuth disabled")
    if not cid:
        raise HTTPException(500, "Missing GOOGLE_CLIENT_ID")
    
    # Validate that redirect_uri was provided
    if not redirect_uri:
        raise HTTPException(400, "redirect_uri parameter is required")
    
    state = secrets.token_urlsafe(24)
    # Store ephemeral state in token store along with redirect_uri for validation
    stored = google_get("__state__") or {}
    stored[state] = {"label": label, "ts": _now(), "redirect_uri": redirect_uri}
    google_set("__state__", stored)
    params = {
        "client_id": cid,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",   # ensures refresh_token on first run
        "state": state,
    }
    return {"authorize_url": f"{GOOGLE_AUTH}?{urlencode(params)}"}

@router.get("/oauth/google/callback")
def google_callback(code: str, state: str):
    enabled, cid, cs, scopes, label_default = _cfg()
    if not enabled:
        raise HTTPException(400, "Google OAuth disabled")

    # Validate state
    state_map = google_get("__state__") or {}
    ctx = state_map.pop(state, None)
    google_set("__state__", state_map)  # remove used state
    if not ctx:
        raise HTTPException(400, "Invalid state")

    label = ctx.get("label") or label_default
    redirect_uri = ctx.get("redirect_uri")
    if not redirect_uri:
        raise HTTPException(400, "Invalid state: missing redirect_uri")

    data = {
        "code": code,
        "client_id": cid,
        "client_secret": cs,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    with httpx.Client(timeout=20) as client:
        r = client.post(GOOGLE_TOKEN, data=data)
        if r.status_code != 200:
            raise HTTPException(400, f"Token exchange failed: {r.text}")
        tok = r.json()

    # Persist refresh + access token
    entry = {
        "access_token": tok.get("access_token"),
        "refresh_token": tok.get("refresh_token"),  # may be None on subsequent grants
        "scope": tok.get("scope"),
        "token_type": tok.get("token_type"),
        "expiry": _now() + int(tok.get("expires_in", 3600)) - 30,  # 30s skew
    }
    # Merge with existing to avoid dropping a good refresh_token
    existing = google_get(label) or {}
    if not entry.get("refresh_token") and existing.get("refresh_token"):
        entry["refresh_token"] = existing["refresh_token"]

    google_set(label, entry)
    return {"status": "ok", "label": label, "has_refresh": bool(entry.get("refresh_token"))}

def _refresh_if_needed(label: str):
    cfg_enabled, cid, cs, scopes, _ = _cfg()
    entry = google_get(label)
    if not entry:
        raise HTTPException(404, f"No token for label '{label}'. Use /oauth to authenticate first.")
    if entry.get("access_token") and entry.get("expiry", 0) > _now():
        return entry

    refresh = entry.get("refresh_token")
    if not refresh:
        raise HTTPException(409, "No refresh_token stored. This usually happens when: 1) Initial OAuth didn't include 'offline' access, 2) Token was revoked, or 3) Refresh token expired. Please re-authenticate via /oauth")

    data = {
        "client_id": cid,
        "client_secret": cs,
        "refresh_token": refresh,
        "grant_type": "refresh_token",
    }
    with httpx.Client(timeout=20) as client:
        r = client.post(GOOGLE_TOKEN, data=data)
        if r.status_code != 200:
            error_details = r.text
            try:
                error_json = r.json()
                if error_json.get("error") == "invalid_grant":
                    # Clear the bad token and provide helpful message
                    google_set(label, {})
                    raise HTTPException(400, "Refresh token has expired or been revoked. The token has been cleared. Please re-authenticate via /oauth to get a new token.")
            except:
                pass
            raise HTTPException(400, f"Refresh failed: {error_details}")
        tok = r.json()

    entry["access_token"] = tok.get("access_token")
    entry["expiry"] = _now() + int(tok.get("expires_in", 3600)) - 30
    # Some providers re-issue refresh_token; Google usually doesn't on refresh
    if tok.get("refresh_token"):
        entry["refresh_token"] = tok.get("refresh_token")
    google_set(label, entry)
    return entry

@router.get("/oauth/google/token")
def google_token(x_api_key: str | None = Header(default=None), label: str | None = None):
    require_api_key(x_api_key)
    _, _, _, _, default_label = _cfg()
    entry = _refresh_if_needed(label or default_label)
    return {
        "access_token": entry["access_token"],
        "expiry": entry["expiry"],
        "token_type": entry.get("token_type", "Bearer"),
        "scope": entry.get("scope"),
    }

@router.get("/oauth/google/status")
def google_status(x_api_key: str | None = Header(default=None), label: str | None = None):
    require_api_key(x_api_key)
    _, _, _, _, default_label = _cfg()
    entry = google_get(label or default_label)
    
    if not entry:
        return {"status": "no_token", "message": "No token found. Please authenticate first."}
    
    has_access = bool(entry.get("access_token"))
    has_refresh = bool(entry.get("refresh_token"))
    expiry = entry.get("expiry", 0)
    is_expired = expiry <= _now()
    
    status = "ok"
    message = "Token is valid and not expired"
    
    if not has_refresh:
        status = "no_refresh_token"
        message = "Missing refresh token. Re-authentication required."
    elif is_expired and not has_access:
        status = "expired_no_access"
        message = "Token expired and no access token available"
    elif is_expired:
        status = "expired"
        message = "Access token expired but can be refreshed"
    
    return {
        "status": status,
        "message": message,
        "has_access_token": has_access,
        "has_refresh_token": has_refresh,
        "expires_at": expiry,
        "expires_in_seconds": max(0, expiry - _now()),
        "is_expired": is_expired,
        "scope": entry.get("scope")
    }

@router.delete("/oauth/google/token")
def google_delete_token(x_api_key: str | None = Header(default=None), label: str | None = None):
    """Delete stored tokens for a label. Use this when tokens are corrupted or you want to start fresh."""
    require_api_key(x_api_key)
    _, _, _, _, default_label = _cfg()
    target_label = label or default_label
    
    entry = google_get(target_label)
    if not entry:
        raise HTTPException(404, f"No token found for label '{target_label}'")
    
    google_set(target_label, {})
    logger.info(f"Deleted tokens for label: {target_label}")
    return {"status": "ok", "message": f"Tokens deleted for label '{target_label}'. Use /oauth to re-authenticate."}
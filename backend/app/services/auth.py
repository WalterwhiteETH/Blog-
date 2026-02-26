from __future__ import annotations

import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import jwt
from fastapi import HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from ..config import settings
from ..schemas import AppUser
from ..store import store

oauth_state_cache: dict[str, float] = {}


def issue_app_token(user: AppUser) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": user.user_id,
        "email": user.email,
        "name": user.name,
        "provider": user.provider,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def decode_app_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


def google_to_user(claims: dict) -> AppUser:
    google_sub = str(claims.get("sub", "")).strip()
    email = str(claims.get("email", "")).strip().lower()
    if not google_sub or not email:
        raise HTTPException(status_code=400, detail="Google token missing sub/email")
    return AppUser(
        user_id=f"google:{google_sub}",
        email=email,
        name=str(claims.get("name", "Google User")),
        picture=claims.get("picture"),
        provider="google",
    )


def verify_google_id_token(raw_id_token: str) -> AppUser:
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID is not configured")
    try:
        claims = google_id_token.verify_oauth2_token(
            raw_id_token, google_requests.Request(), settings.google_client_id
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid Google ID token") from exc
    return google_to_user(claims)


def exchange_google_code_for_tokens(code: str) -> dict:
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth credentials are not configured")
    body = urlencode(
        {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")
    request = Request(
        "https://oauth2.googleapis.com/token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Google OAuth code exchange failed") from exc


def build_google_auth_url() -> dict[str, str]:
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID is not configured")
    state = secrets.token_urlsafe(24)
    oauth_state_cache[state] = time.time()
    now = time.time()
    for key, created_at in list(oauth_state_cache.items()):
        if now - created_at > 600:
            oauth_state_cache.pop(key, None)

    params = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
    )
    return {
        "auth_url": f"https://accounts.google.com/o/oauth2/v2/auth?{params}",
        "state": state,
    }


def consume_oauth_state(state: str) -> None:
    created_at = oauth_state_cache.pop(state, None)
    if created_at is None or time.time() - created_at > 600:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")


def login_with_google_id_token(raw_id_token: str) -> dict[str, object]:
    user = verify_google_id_token(raw_id_token)
    store.user_profiles[user.user_id] = user
    store.save_state()
    return {"user": user, "access_token": issue_app_token(user), "token_type": "bearer"}

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    client_url: str = os.getenv("CLIENT_URL", "http://localhost:5173")
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    lastfm_api_key: str = os.getenv("LASTFM_API_KEY", "")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv(
        "GOOGLE_REDIRECT_URI", "http://localhost:8787/api/auth/google/callback"
    )
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
    jwt_expires_minutes: int = int(os.getenv("JWT_EXPIRES_MINUTES", "1440"))

    backend_dir: Path = Path(__file__).resolve().parents[1]
    data_dir: Path = backend_dir / "data"
    state_file: Path = data_dir / "state.json"


settings = Settings()

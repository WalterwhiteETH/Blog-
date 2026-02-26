from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


class PlaylistCreate(BaseModel):
    name: str
    creator: str
    genre: str
    price: float
    cover: HttpUrl
    seller_user_id: Optional[str] = None
    song_ids: list[int] = Field(default_factory=list)


class Playlist(PlaylistCreate):
    id: int
    distribution: Literal["free_share", "paid_sale"] = "paid_sale"
    rights_status: Literal["verified", "not_required"] = "not_required"
    supporting_artists: list[str] = Field(default_factory=list)
    markets: list[str] = Field(default_factory=list)
    age_min: int = 13
    age_max: int = 65
    quality_score: float = 0.6
    trend_score: float = 0.5


class CheckoutRequest(BaseModel):
    playlistId: int


class Song(BaseModel):
    id: int
    title: str
    artist_id: str
    artist_name: str
    genre: str
    tier: Literal["free", "premium"] = "free"
    price: float = 0.0


class PurchaseSongRequest(BaseModel):
    user_id: str
    song_id: int


class SupportArtistRequest(BaseModel):
    user_id: str
    artist_id: str
    amount: float = Field(default=1, gt=0)


class GoogleIdTokenRequest(BaseModel):
    id_token: str


class AppUser(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[HttpUrl] = None
    provider: Literal["google"] = "google"


class RecommendationRequest(BaseModel):
    age: int = Field(ge=13, le=100)
    location: str
    limit: int = Field(default=8, ge=1, le=20)
    listen_now_genres: list[str] = Field(default_factory=list)
    previous_listening_genres: list[str] = Field(default_factory=list)
    previous_listing_history: list[int] = Field(default_factory=list)
    market_strategy: Literal["balanced", "growth", "retention", "premium"] = "balanced"
    include_youtube: bool = True
    include_lastfm: bool = True


class RecommendationItem(BaseModel):
    playlist: Playlist
    score: float
    reasons: list[str]


class YouTubeTrack(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail: HttpUrl
    views: int
    published_at: str


class LastFmTrack(BaseModel):
    name: str
    artist: str
    url: str
    listeners: int
    image: Optional[HttpUrl] = None


class RecommendationSections(BaseModel):
    blended: list[RecommendationItem]
    listen_now: list[RecommendationItem]
    previous_history: list[RecommendationItem]
    location_based: list[RecommendationItem]
    trending: list[RecommendationItem]

from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Header, HTTPException

from .config import settings
from .schemas import (
    CheckoutRequest,
    GoogleIdTokenRequest,
    Playlist,
    PlaylistCreate,
    PurchaseSongRequest,
    RecommendationRequest,
    Song,
    SupportArtistRequest,
)
from .services.auth import (
    build_google_auth_url,
    consume_oauth_state,
    decode_app_token,
    exchange_google_code_for_tokens,
    login_with_google_id_token,
)
from .services.recommendation import build_recommendation_response
from .store import store

router = APIRouter(prefix="/api")


def _user_has_song_rights(user_id: str, song: Song) -> bool:
    if song.tier == "free":
        return True
    if song.id in store.user_song_purchases.get(user_id, set()):
        return True
    if song.artist_id in store.user_artist_support.get(user_id, set()):
        return True
    return False


def _validate_playlist_rights(user_id: str, selected_songs: list[Song]) -> tuple[bool, list[str], list[str]]:
    missing_song_titles: list[str] = []
    supporting_artists: set[str] = set()
    for song in selected_songs:
        supporting_artists.add(song.artist_id)
        if not _user_has_song_rights(user_id, song):
            missing_song_titles.append(song.title)
    return (len(missing_song_titles) == 0, missing_song_titles, sorted(supporting_artists))


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "ok": True,
        "service": "music-lite-api",
        "listings_count": len(store.listings),
        "songs_count": len(store.songs_catalog),
    }


@router.get("/auth/google/url")
def auth_google_url() -> dict[str, str]:
    return build_google_auth_url()


@router.get("/auth/google/callback")
def auth_google_callback(code: str, state: str) -> dict[str, object]:
    consume_oauth_state(state)
    token_payload = exchange_google_code_for_tokens(code)
    raw_id_token = token_payload.get("id_token")
    if not raw_id_token:
        raise HTTPException(status_code=401, detail="Google response missing ID token")
    return login_with_google_id_token(raw_id_token)


@router.post("/auth/google/verify")
def auth_google_verify(payload: GoogleIdTokenRequest) -> dict[str, object]:
    return login_with_google_id_token(payload.id_token)


@router.get("/auth/me")
def auth_me(authorization: Optional[str] = Header(default=None)) -> dict[str, object]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    claims = decode_app_token(token)
    user = store.user_profiles.get(str(claims.get("sub", "")))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


@router.get("/playlists")
def get_playlists() -> dict[str, list[Playlist]]:
    return {"listings": store.listings}


@router.get("/catalog/songs")
def get_songs_catalog(tier: Optional[Literal["free", "premium"]] = None) -> dict[str, list[Song]]:
    if tier is None:
        return {"songs": store.songs_catalog}
    return {"songs": [song for song in store.songs_catalog if song.tier == tier]}


@router.post("/purchase-song")
def purchase_song(payload: PurchaseSongRequest) -> dict[str, object]:
    song = store.find_song(payload.song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    if song.tier == "free":
        return {"ok": True, "message": "Free song does not require purchase", "song": song}
    store.user_song_purchases[payload.user_id].add(song.id)
    store.save_state()
    return {"ok": True, "message": "Song purchased", "song": song}


@router.post("/support-artist")
def support_artist(payload: SupportArtistRequest) -> dict[str, object]:
    artist_id = payload.artist_id.strip()
    if not artist_id:
        raise HTTPException(status_code=400, detail="artist_id is required")
    store.user_artist_support[payload.user_id].add(artist_id)
    store.save_state()
    return {
        "ok": True,
        "message": "Artist support recorded",
        "artist_id": artist_id,
        "amount": payload.amount,
    }


@router.get("/users/{user_id}/rights")
def get_user_rights(user_id: str) -> dict[str, object]:
    return {
        "user_id": user_id,
        "purchased_song_ids": sorted(list(store.user_song_purchases.get(user_id, set()))),
        "supported_artist_ids": sorted(list(store.user_artist_support.get(user_id, set()))),
    }


@router.post("/playlists", status_code=201)
def create_playlist(payload: PlaylistCreate) -> dict[str, Playlist]:
    if payload.price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")
    selected_songs = [store.find_song(song_id) for song_id in payload.song_ids]
    if any(song is None for song in selected_songs):
        raise HTTPException(status_code=400, detail="One or more song_ids are invalid")
    selected_songs = [song for song in selected_songs if song is not None]
    seller_user_id = (payload.seller_user_id or "").strip()
    name = payload.name.strip()
    creator = payload.creator.strip()
    genre = payload.genre.strip()
    if not seller_user_id:
        raise HTTPException(status_code=400, detail="seller_user_id is required")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    if not creator:
        raise HTTPException(status_code=400, detail="creator is required")
    if not genre:
        raise HTTPException(status_code=400, detail="genre is required")
    if not selected_songs:
        raise HTTPException(status_code=400, detail="song_ids are required")

    only_free_songs = all(song.tier == "free" for song in selected_songs)
    has_any_premium = any(song.tier == "premium" for song in selected_songs)
    if only_free_songs:
        final_price = 0.0
        distribution: Literal["free_share", "paid_sale"] = "free_share"
        rights_status: Literal["verified", "not_required"] = "not_required"
        supporting_artists = sorted({song.artist_id for song in selected_songs})
    else:
        if payload.price <= 0:
            raise HTTPException(status_code=400, detail="Premium/mixed playlists must have price > 0")
        has_rights, missing_titles, supporting_artists = _validate_playlist_rights(
            seller_user_id, selected_songs
        )
        if has_any_premium and not has_rights:
            raise HTTPException(
                status_code=403,
                detail="Cannot sell playlist. Buy songs or support artists first. Missing rights for: "
                + ", ".join(missing_titles),
            )
        final_price = payload.price
        distribution = "paid_sale"
        rights_status = "verified"

    listing = Playlist(
        id=store.next_playlist_id(),
        name=name,
        creator=creator,
        genre=genre,
        price=final_price,
        cover=payload.cover,
        seller_user_id=seller_user_id,
        song_ids=payload.song_ids,
        distribution=distribution,
        rights_status=rights_status,
        supporting_artists=supporting_artists,
        markets=["global"],
        age_min=13,
        age_max=65,
        quality_score=0.58,
        trend_score=0.52,
    )
    store.listings.insert(0, listing)
    store.save_state()
    return {"listing": listing}


@router.post("/recommendations")
def get_recommendations(payload: RecommendationRequest) -> dict[str, object]:
    return build_recommendation_response(payload, store.listings)


@router.post("/checkout-session")
def checkout_session(payload: CheckoutRequest) -> dict[str, str | bool]:
    listing = store.find_listing(payload.playlistId)
    if listing is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if listing.price <= 0:
        raise HTTPException(status_code=400, detail="Playlist has no price yet")
    if not settings.stripe_secret_key:
        return {
            "demo": True,
            "message": "Stripe is not configured yet. Add STRIPE_SECRET_KEY to enable real checkout.",
        }
    return {"demo": True, "message": "Stripe key found. Hook real session creation next."}


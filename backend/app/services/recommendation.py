from __future__ import annotations

from .external_sources import (
    fetch_lastfm_geo_top_tracks,
    fetch_lastfm_tag_top_tracks,
    fetch_youtube_popular_music,
)
from ..schemas import Playlist, RecommendationItem, RecommendationRequest

AGE_GENRE_AFFINITY: dict[str, list[str]] = {
    "13-17": ["Pop", "Hip-Hop", "Afrobeats", "Amapiano"],
    "18-24": ["Hip-Hop", "Afrobeats", "Pop", "Amapiano", "Latin"],
    "25-34": ["Afrobeats", "Pop", "Hip-Hop", "Lo-fi", "Latin"],
    "35-44": ["Pop", "Lo-fi", "Classical", "Latin", "Ambient"],
    "45+": ["Classical", "Ambient", "Lo-fi", "Pop"],
}

MARKET_SEGMENTS: dict[str, str] = {
    "us": "mature",
    "uk": "mature",
    "ca": "mature",
    "de": "mature",
    "fr": "mature",
    "mx": "growth",
    "br": "growth",
    "ng": "growth",
    "gh": "growth",
    "ke": "growth",
    "za": "growth",
    "in": "growth",
    "global": "mixed",
}

LOCATION_GENRE_AFFINITY: dict[str, list[str]] = {
    "us": ["Hip-Hop", "Pop", "R&B", "Latin"],
    "ca": ["Pop", "Hip-Hop", "Lo-fi"],
    "uk": ["Hip-Hop", "Amapiano", "Pop"],
    "ng": ["Afrobeats", "Amapiano", "Hip-Hop"],
    "gh": ["Afrobeats", "Amapiano"],
    "ke": ["Afrobeats", "Amapiano"],
    "za": ["Amapiano", "Afrobeats", "House"],
    "mx": ["Latin", "Pop"],
    "br": ["Latin", "Pop"],
    "fr": ["Hip-Hop", "Pop"],
    "de": ["Techno", "Pop", "Classical"],
    "in": ["Bollywood", "Pop", "Lo-fi"],
}

LOCATION_ALIASES: dict[str, str] = {
    "united states": "us",
    "usa": "us",
    "america": "us",
    "united kingdom": "uk",
    "england": "uk",
    "nigeria": "ng",
    "ghana": "gh",
    "kenya": "ke",
    "south africa": "za",
    "mexico": "mx",
    "brazil": "br",
    "france": "fr",
    "germany": "de",
    "india": "in",
}


def age_bucket(age: int) -> str:
    if age <= 17:
        return "13-17"
    if age <= 24:
        return "18-24"
    if age <= 34:
        return "25-34"
    if age <= 44:
        return "35-44"
    return "45+"


def extract_market_key(location: str) -> str:
    normalized = LOCATION_ALIASES.get(location.strip().lower(), location.strip().lower())
    for token in normalized.replace(",", " ").split():
        if token in LOCATION_GENRE_AFFINITY:
            return token
    for alias, market in LOCATION_ALIASES.items():
        if alias in normalized:
            return market
    return "global"


def normalize_genres(genres: list[str]) -> set[str]:
    return {genre.strip().lower() for genre in genres if genre.strip()}


def strategy_weights(strategy: str, market: str) -> dict[str, float]:
    segment = MARKET_SEGMENTS.get(market, "mixed")
    if strategy == "growth":
        return {"age": 0.14, "location": 0.2, "listen_now": 0.2, "history": 0.14, "listing": 0.08, "trend": 0.18, "quality": 0.04, "market_fit": 0.02}
    if strategy == "retention":
        return {"age": 0.16, "location": 0.14, "listen_now": 0.24, "history": 0.2, "listing": 0.12, "trend": 0.08, "quality": 0.04, "market_fit": 0.02}
    if strategy == "premium":
        return {"age": 0.16, "location": 0.12, "listen_now": 0.16, "history": 0.14, "listing": 0.1, "trend": 0.08, "quality": 0.2, "market_fit": 0.04}
    if segment == "growth":
        return {"age": 0.16, "location": 0.18, "listen_now": 0.2, "history": 0.16, "listing": 0.1, "trend": 0.12, "quality": 0.06, "market_fit": 0.02}
    return {"age": 0.18, "location": 0.18, "listen_now": 0.2, "history": 0.16, "listing": 0.1, "trend": 0.1, "quality": 0.06, "market_fit": 0.02}


def advanced_score(
    playlist: Playlist,
    payload: RecommendationRequest,
    all_listings: list[Playlist],
    history_genres: set[str],
    listen_now_genres: set[str],
    history_listing_ids: set[int],
) -> RecommendationItem:
    market = extract_market_key(payload.location)
    age_pref = {g.lower() for g in AGE_GENRE_AFFINITY.get(age_bucket(payload.age), [])}
    loc_pref = {g.lower() for g in LOCATION_GENRE_AFFINITY.get(market, LOCATION_GENRE_AFFINITY.get("us", []))}
    genre = playlist.genre.lower()
    weights = strategy_weights(payload.market_strategy, market)

    age_score = 1.0 if genre in age_pref else 0.45
    location_score = 1.0 if genre in loc_pref else 0.5
    listen_now_score = 1.0 if (listen_now_genres and genre in listen_now_genres) else 0.55
    history_score = 1.0 if (history_genres and genre in history_genres) else 0.52
    listing_history_boost = 0.5
    if playlist.id in history_listing_ids:
        listing_history_boost = 1.0
    elif history_listing_ids:
        hist_genres_from_ids = {p.genre.lower() for p in all_listings if p.id in history_listing_ids}
        if genre in hist_genres_from_ids:
            listing_history_boost = 0.82
    market_fit_score = 1.0 if ("global" in playlist.markets or market in playlist.markets) else 0.42

    score = (
        age_score * weights["age"]
        + location_score * weights["location"]
        + listen_now_score * weights["listen_now"]
        + history_score * weights["history"]
        + listing_history_boost * weights["listing"]
        + playlist.trend_score * weights["trend"]
        + playlist.quality_score * weights["quality"]
        + market_fit_score * weights["market_fit"]
    )

    reasons: list[str] = []
    if genre in listen_now_genres:
        reasons.append("Matches Listen Now taste")
    if genre in history_genres:
        reasons.append("Matches previous listening history")
    if genre in loc_pref:
        reasons.append(f"Popular in {market.upper()}")
    if playlist.id in history_listing_ids:
        reasons.append("Seen in previous listing history")
    if playlist.trend_score >= 0.85:
        reasons.append("Strong trending signal")
    if playlist.quality_score >= 0.85:
        reasons.append("High quality curation")
    if not reasons:
        reasons.append("General relevance match")

    return RecommendationItem(playlist=playlist, score=round(score, 4), reasons=reasons[:3])


def rank_for_section(candidates: list[Playlist], scorer, limit: int) -> list[RecommendationItem]:
    return sorted([scorer(item) for item in candidates], key=lambda x: x.score, reverse=True)[:limit]


def build_recommendation_response(payload: RecommendationRequest, listings: list[Playlist]) -> dict[str, object]:
    candidates = [item for item in listings if payload.age >= item.age_min and payload.age <= item.age_max] or listings
    listen_now_genres = normalize_genres(payload.listen_now_genres)
    history_genres = normalize_genres(payload.previous_listening_genres)
    history_listing_ids = set(payload.previous_listing_history)
    market = extract_market_key(payload.location)
    location_genres = {g.lower() for g in LOCATION_GENRE_AFFINITY.get(market, [])}

    scorer = lambda item: advanced_score(item, payload, listings, history_genres, listen_now_genres, history_listing_ids)
    blended = rank_for_section(candidates, scorer, payload.limit)
    listen_now = rank_for_section([c for c in candidates if c.genre.lower() in listen_now_genres] or candidates, scorer, payload.limit)
    previous_history = rank_for_section([c for c in candidates if c.genre.lower() in history_genres] or candidates, scorer, payload.limit)
    location_based = rank_for_section([c for c in candidates if c.genre.lower() in location_genres] or candidates, scorer, payload.limit)
    trending = rank_for_section(
        candidates,
        lambda item: RecommendationItem(
            playlist=item,
            score=round(item.trend_score * 0.65 + item.quality_score * 0.35, 4),
            reasons=["Trending now", "Quality filtered"],
        ),
        payload.limit,
    )
    response: dict[str, object] = {
        "sections": {
            "blended": blended,
            "listen_now": listen_now,
            "previous_history": previous_history,
            "location_based": location_based,
            "trending": trending,
        },
        "recommendations": blended,
    }
    if payload.include_youtube:
        response["youtube_popular"] = fetch_youtube_popular_music(market, payload.limit)
    if payload.include_lastfm:
        tags = list(listen_now_genres | history_genres | location_genres)
        response["lastfm"] = {
            "location_top": fetch_lastfm_geo_top_tracks(market, payload.limit),
            "taste_top": fetch_lastfm_tag_top_tracks(tags, payload.limit),
        }
    return response

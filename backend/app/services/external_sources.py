from __future__ import annotations

import json
import time
from urllib.parse import urlencode
from urllib.request import urlopen

from ..config import settings
from ..schemas import LastFmTrack, YouTubeTrack

YOUTUBE_REGION_MAP: dict[str, str] = {
    "uk": "GB",
    "global": "US",
}
YOUTUBE_CACHE_TTL_SECONDS = 600
youtube_cache: dict[str, tuple[float, list[YouTubeTrack]]] = {}

LASTFM_CACHE_TTL_SECONDS = 600
lastfm_cache: dict[str, tuple[float, list[LastFmTrack]]] = {}
LASTFM_COUNTRY_MAP: dict[str, str] = {
    "us": "United States",
    "uk": "United Kingdom",
    "ca": "Canada",
    "de": "Germany",
    "fr": "France",
    "mx": "Mexico",
    "br": "Brazil",
    "ng": "Nigeria",
    "gh": "Ghana",
    "ke": "Kenya",
    "za": "South Africa",
    "in": "India",
    "global": "United States",
}


def youtube_region_from_market(market: str) -> str:
    if market in YOUTUBE_REGION_MAP:
        return YOUTUBE_REGION_MAP[market]
    return market.upper()[:2]


def lastfm_country_from_market(market: str) -> str:
    return LASTFM_COUNTRY_MAP.get(market, "United States")


def youtube_fallback(limit: int) -> list[YouTubeTrack]:
    return [
        YouTubeTrack(
            video_id="dQw4w9WgXcQ",
            title="Popular Music Trending (Fallback)",
            channel="Music Lite",
            thumbnail="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            views=0,
            published_at="1970-01-01T00:00:00Z",
        )
    ][:limit]


def lastfm_fallback(limit: int) -> list[LastFmTrack]:
    return [
        LastFmTrack(
            name="Last.fm unavailable",
            artist="Music Lite",
            url="https://www.last.fm",
            listeners=0,
            image=None,
        )
    ][:limit]


def parse_lastfm_tracks(items: list[dict]) -> list[LastFmTrack]:
    tracks: list[LastFmTrack] = []
    for item in items:
        images = item.get("image", [])
        image_url = None
        if isinstance(images, list):
            for candidate in reversed(images):
                maybe = candidate.get("#text")
                if maybe:
                    image_url = maybe
                    break
        artist_obj = item.get("artist", {})
        artist_name = artist_obj.get("name") if isinstance(artist_obj, dict) else str(artist_obj)
        try:
            listeners_int = int(str(item.get("listeners", "0")))
        except ValueError:
            listeners_int = 0
        tracks.append(
            LastFmTrack(
                name=item.get("name", "Unknown"),
                artist=artist_name or "Unknown",
                url=item.get("url", "https://www.last.fm"),
                listeners=listeners_int,
                image=image_url,
            )
        )
    return tracks


def fetch_youtube_popular_music(market: str, limit: int) -> list[YouTubeTrack]:
    if not settings.youtube_api_key:
        return youtube_fallback(limit)
    region_code = youtube_region_from_market(market)
    cache_key = f"{region_code}:{limit}"
    now = time.time()
    cached = youtube_cache.get(cache_key)
    if cached and now - cached[0] < YOUTUBE_CACHE_TTL_SECONDS:
        return cached[1]

    params = urlencode(
        {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "videoCategoryId": "10",
            "maxResults": str(limit),
            "regionCode": region_code,
            "key": settings.youtube_api_key,
        }
    )
    try:
        with urlopen(f"https://www.googleapis.com/youtube/v3/videos?{params}", timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        items = payload.get("items", [])
        tracks: list[YouTubeTrack] = []
        for item in items:
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            thumbnails = snippet.get("thumbnails", {})
            thumb = (
                thumbnails.get("high", {}).get("url")
                or thumbnails.get("medium", {}).get("url")
                or thumbnails.get("default", {}).get("url")
            )
            if not thumb:
                continue
            tracks.append(
                YouTubeTrack(
                    video_id=item.get("id", ""),
                    title=snippet.get("title", "Unknown title"),
                    channel=snippet.get("channelTitle", "Unknown channel"),
                    thumbnail=thumb,
                    views=int(statistics.get("viewCount", 0)),
                    published_at=snippet.get("publishedAt", ""),
                )
            )
        if tracks:
            youtube_cache[cache_key] = (now, tracks)
            return tracks
    except Exception:
        pass
    return youtube_fallback(limit)


def fetch_lastfm_geo_top_tracks(market: str, limit: int) -> list[LastFmTrack]:
    if not settings.lastfm_api_key:
        return lastfm_fallback(limit)
    country = lastfm_country_from_market(market)
    cache_key = f"geo:{country}:{limit}"
    now = time.time()
    cached = lastfm_cache.get(cache_key)
    if cached and now - cached[0] < LASTFM_CACHE_TTL_SECONDS:
        return cached[1]
    params = urlencode(
        {
            "method": "geo.gettoptracks",
            "country": country,
            "api_key": settings.lastfm_api_key,
            "format": "json",
            "limit": str(limit),
        }
    )
    try:
        with urlopen(f"https://ws.audioscrobbler.com/2.0/?{params}", timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        parsed = parse_lastfm_tracks(payload.get("tracks", {}).get("track", []))
        if parsed:
            lastfm_cache[cache_key] = (now, parsed)
            return parsed
    except Exception:
        pass
    return lastfm_fallback(limit)


def fetch_lastfm_tag_top_tracks(tags: list[str], limit: int) -> list[LastFmTrack]:
    if not settings.lastfm_api_key:
        return lastfm_fallback(limit)
    canonical = sorted({tag.strip().lower() for tag in tags if tag.strip()})
    if not canonical:
        return []
    cache_key = f"tag:{'|'.join(canonical)}:{limit}"
    now = time.time()
    cached = lastfm_cache.get(cache_key)
    if cached and now - cached[0] < LASTFM_CACHE_TTL_SECONDS:
        return cached[1]

    collected: list[LastFmTrack] = []
    seen: set[str] = set()
    per_tag = max(1, min(4, limit))
    try:
        for tag in canonical[:3]:
            params = urlencode(
                {
                    "method": "tag.gettoptracks",
                    "tag": tag,
                    "api_key": settings.lastfm_api_key,
                    "format": "json",
                    "limit": str(per_tag),
                }
            )
            with urlopen(f"https://ws.audioscrobbler.com/2.0/?{params}", timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
            for track in parse_lastfm_tracks(payload.get("tracks", {}).get("track", [])):
                key = f"{track.name.lower()}::{track.artist.lower()}"
                if key in seen:
                    continue
                seen.add(key)
                collected.append(track)
                if len(collected) >= limit:
                    lastfm_cache[cache_key] = (now, collected)
                    return collected
    except Exception:
        return collected or lastfm_fallback(limit)

    lastfm_cache[cache_key] = (now, collected)
    return collected

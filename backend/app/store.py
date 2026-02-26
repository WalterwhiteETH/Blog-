from __future__ import annotations

import json
import threading
from collections import defaultdict
from typing import Optional

from .config import settings
from .schemas import AppUser, Playlist, Song
from .seeds import seed_listings, seed_songs


class InMemoryStore:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.listings: list[Playlist] = [Playlist(**item.model_dump()) for item in seed_listings()]
        self.songs_catalog: list[Song] = seed_songs()
        self.user_song_purchases: dict[str, set[int]] = defaultdict(set)
        self.user_artist_support: dict[str, set[str]] = defaultdict(set)
        self.user_profiles: dict[str, AppUser] = {}
        self.load_state()

    def load_state(self) -> None:
        if not settings.state_file.exists():
            return
        try:
            payload = json.loads(settings.state_file.read_text(encoding="utf-8"))
            stored_listings = payload.get("listings", [])
            if isinstance(stored_listings, list):
                self.listings = [Playlist(**item) for item in stored_listings]

            stored_purchases = payload.get("user_song_purchases", {})
            if isinstance(stored_purchases, dict):
                self.user_song_purchases.clear()
                for user_id, song_ids in stored_purchases.items():
                    self.user_song_purchases[user_id] = set(int(song_id) for song_id in song_ids)

            stored_support = payload.get("user_artist_support", {})
            if isinstance(stored_support, dict):
                self.user_artist_support.clear()
                for user_id, artist_ids in stored_support.items():
                    self.user_artist_support[user_id] = set(str(artist_id) for artist_id in artist_ids)

            stored_profiles = payload.get("user_profiles", {})
            if isinstance(stored_profiles, dict):
                self.user_profiles.clear()
                for user_id, profile in stored_profiles.items():
                    self.user_profiles[user_id] = AppUser(**profile)
        except Exception:
            # Keep service available with seed data.
            self.listings = [Playlist(**item.model_dump()) for item in seed_listings()]

    def save_state(self) -> None:
        with self.lock:
            settings.data_dir.mkdir(parents=True, exist_ok=True)
            payload = {
                "listings": [item.model_dump(mode="json") for item in self.listings],
                "user_song_purchases": {
                    user_id: sorted(list(song_ids))
                    for user_id, song_ids in self.user_song_purchases.items()
                },
                "user_artist_support": {
                    user_id: sorted(list(artist_ids))
                    for user_id, artist_ids in self.user_artist_support.items()
                },
                "user_profiles": {
                    user_id: profile.model_dump(mode="json")
                    for user_id, profile in self.user_profiles.items()
                },
            }
            settings.state_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def find_listing(self, playlist_id: int) -> Optional[Playlist]:
        for item in self.listings:
            if item.id == playlist_id:
                return item
        return None

    def find_song(self, song_id: int) -> Optional[Song]:
        for song in self.songs_catalog:
            if song.id == song_id:
                return song
        return None

    def next_playlist_id(self) -> int:
        return max([item.id for item in self.listings], default=0) + 1


store = InMemoryStore()

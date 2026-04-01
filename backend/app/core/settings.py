from functools import lru_cache


def _get_env(name: str, default: str) -> str:
    import os

    return os.getenv(name, default)


def _get_bool(name: str, default: bool) -> bool:
    raw = _get_env(name, 'true' if default else 'false')
    return raw.strip().lower() in {'1', 'true', 'yes', 'on'}


class AppSettings:
    def __init__(self) -> None:
        self.app_env = _get_env('APP_ENV', 'development')
        self.app_title = _get_env('APP_TITLE', 'Music Platform Backend')
        self.app_version = _get_env('APP_VERSION', '1.0.0')
        self.admin_api_key = _get_env('ADMIN_API_KEY', 'admin123')
        self.database_url = _get_env('DATABASE_URL', 'sqlite:///./music_platform.db')
        self.database_echo = _get_bool('DATABASE_ECHO', False)

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith('sqlite')


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()

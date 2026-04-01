from app.core.settings import AppSettings


def test_settings_defaults() -> None:
    settings = AppSettings()

    assert settings.app_title == 'Music Platform Backend'
    assert settings.app_version == '1.0.0'
    assert settings.admin_api_key
    assert settings.database_url

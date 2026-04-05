"""
Extended settings for the standalone payment domain.
"""

from functools import lru_cache

from app.core.settings import AppSettings, _get_bool, _get_env


class PaymentSettings(AppSettings):
    """Application settings extended with active payment-provider configuration."""

    def __init__(self) -> None:
        super().__init__()

        self.payment_enabled = _get_bool("PAYMENT_ENABLED", True)
        self.payment_default_currency = (_get_env("PAYMENT_DEFAULT_CURRENCY", "ETB") or "ETB").upper()

        self.telebirr_enabled = _get_bool("TELEBIRR_ENABLED", False)
        self.telebirr_base_url = _get_env("TELEBIRR_BASE_URL", "https://api.telebirr.et") or "https://api.telebirr.et"
        self.telebirr_app_id = _get_env("TELEBIRR_APP_ID", "")
        self.telebirr_app_secret = _get_env("TELEBIRR_APP_SECRET", "")
        self.telebirr_merchant_code = _get_env("TELEBIRR_MERCHANT_CODE", "")
        self.telebirr_short_code = _get_env("TELEBIRR_SHORT_CODE", "")
        self.telebirr_notify_url = _get_env("TELEBIRR_NOTIFY_URL")
        self.telebirr_return_url = _get_env("TELEBIRR_RETURN_URL")
        self.telebirr_test_mode = _get_bool("TELEBIRR_TEST_MODE", True)

        self.mpesa_enabled = _get_bool("MPESA_ENABLED", False)
        self.mpesa_base_url = (
            _get_env("MPESA_BASE_URL", "https://sandbox.safaricom.co.ke")
            or "https://sandbox.safaricom.co.ke"
        )
        self.mpesa_consumer_key = _get_env("MPESA_CONSUMER_KEY", "")
        self.mpesa_consumer_secret = _get_env("MPESA_CONSUMER_SECRET", "")
        self.mpesa_short_code = _get_env("MPESA_SHORT_CODE", "")
        self.mpesa_passkey = _get_env("MPESA_PASSKEY", "")
        self.mpesa_callback_url = _get_env("MPESA_CALLBACK_URL")
        self.mpesa_initiator_name = _get_env("MPESA_INITIATOR_NAME")
        self.mpesa_security_credential = _get_env("MPESA_SECURITY_CREDENTIAL")
        self.mpesa_test_mode = _get_bool("MPESA_TEST_MODE", True)

        self._validate_payment_settings()

    def _validate_payment_settings(self) -> None:
        if len(self.payment_default_currency) != 3:
            raise ValueError("PAYMENT_DEFAULT_CURRENCY must be a 3-letter currency code")

        if self.telebirr_enabled:
            required_telebirr = [
                "telebirr_app_id",
                "telebirr_app_secret",
                "telebirr_merchant_code",
                "telebirr_short_code",
            ]
            for setting in required_telebirr:
                if not getattr(self, setting):
                    raise ValueError(f"TELEBIRR_ENABLED requires {setting.upper()}")

        if self.mpesa_enabled:
            required_mpesa = [
                "mpesa_consumer_key",
                "mpesa_consumer_secret",
                "mpesa_short_code",
                "mpesa_passkey",
            ]
            for setting in required_mpesa:
                if not getattr(self, setting):
                    raise ValueError(f"MPESA_ENABLED requires {setting.upper()}")

    def get_enabled_providers(self) -> list[str]:
        providers: list[str] = []
        if self.telebirr_enabled:
            providers.append("telebirr")
        if self.mpesa_enabled:
            providers.append("mpesa")
        return providers

    def is_provider_enabled(self, provider_name: str) -> bool:
        return provider_name in self.get_enabled_providers()


@lru_cache(maxsize=1)
def get_payment_settings() -> PaymentSettings:
    return PaymentSettings()


def get_settings() -> PaymentSettings:
    return get_payment_settings()

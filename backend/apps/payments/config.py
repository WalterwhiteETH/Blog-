"""
Payment domain configuration.

This module configures payment providers, services, and other
payment domain components without import-time side effects.
"""

from typing import Dict, Any, Optional, List

from app.core.settings import get_settings
from apps.payments.providers.base import BasePaymentProvider
from apps.payments.providers.telebirr import TelebirrProvider
from apps.payments.providers.telebirr_h5 import TelebirrH5Provider
from apps.payments.providers.telebirr_official import TelebirrOfficialProvider
from apps.payments.providers.mpesa import MpesaProvider
from shared.logging import get_logger

logger = get_logger(__name__)


class PaymentConfig:
    """
    Payment domain configuration.
    
    This class manages payment provider configurations and
    provides factory methods for creating provider instances.
    """
    
    def __init__(self, settings: Optional[Any] = None):
        self.settings = settings or get_settings()
        self._provider_configs = self._load_provider_configs()
    
    def _load_provider_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load provider configurations from settings."""
        configs = {}
        
        # Telebirr configuration
        if hasattr(self.settings, 'telebirr_enabled') and self.settings.telebirr_enabled:
            configs["telebirr"] = {
                "base_url": getattr(self.settings, 'telebirr_base_url', "https://api.telebirr.et"),
                "app_id": getattr(self.settings, 'telebirr_app_id', ""),
                "app_secret": getattr(self.settings, 'telebirr_app_secret', ""),
                "merchant_code": getattr(self.settings, 'telebirr_merchant_code', ""),
                "short_code": getattr(self.settings, 'telebirr_short_code', ""),
                "test_mode": getattr(self.settings, 'telebirr_test_mode', True),
            }
        
        return configs
    
    def get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific provider."""
        return self._provider_configs.get(provider_name)
    
    def create_provider(self, provider_name: str) -> Optional[BasePaymentProvider]:
        """Create a provider instance."""
        config = self.get_provider_config(provider_name)
        if not config:
            logger.warning(f"No configuration found for provider: {provider_name}")
            return None
        
        if provider_name == "telebirr":
            return TelebirrProvider(config)
        elif provider_name == "telebirr_h5":
            return TelebirrH5Provider(config)
        elif provider_name == "telebirr_official":
            return TelebirrOfficialProvider(config)
        elif provider_name == "mpesa":
            return MpesaProvider(config)
        
        logger.error(f"Unknown provider: {provider_name}")
        return None
    
    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled provider names."""
        return list(self._provider_configs.keys())


# Global config instance - created lazily
_payment_config: Optional[PaymentConfig] = None


def get_payment_config() -> PaymentConfig:
    """Get the global payment configuration instance."""
    global _payment_config
    if _payment_config is None:
        _payment_config = PaymentConfig()
    return _payment_config


def initialize_payment_providers() -> Dict[str, BasePaymentProvider]:
    """Initialize all enabled payment providers."""
    config = get_payment_config()
    providers = {}
    
    for provider_name in config.get_enabled_providers():
        provider = config.create_provider(provider_name)
        if provider:
            providers[provider_name] = provider
            logger.info(f"Initialized payment provider: {provider_name}")
        else:
            logger.error(f"Failed to initialize provider: {provider_name}")
    
    return providers


def extend_settings_with_payment(settings: Any) -> Any:
    """Extend settings with payment-specific configuration."""
    # Add payment settings with safe defaults
    settings.telebirr_enabled = getattr(settings, 'telebirr_enabled', False)
    settings.telebirr_base_url = getattr(settings, 'telebirr_base_url', "https://api.telebirr.et")
    settings.telebirr_app_id = getattr(settings, 'telebirr_app_id', "")
    settings.telebirr_app_secret = getattr(settings, 'telebirr_app_secret', "")
    settings.telebirr_merchant_code = getattr(settings, 'telebirr_merchant_code', "")
    settings.telebirr_short_code = getattr(settings, 'telebirr_short_code', "")
    settings.telebirr_test_mode = getattr(settings, 'telebirr_test_mode', True)
    
    return settings

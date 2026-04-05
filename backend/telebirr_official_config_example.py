"""
Telebirr Official Configuration Example

This file shows how to configure the official Telebirr H5 provider
based on Ethiopian Telecom's actual API specification.
"""

# Example configuration for Telebirr Official H5 Integration
TELEBIRR_OFFICIAL_CONFIG = {
    # Required credentials from Ethiopian Telecom developer portal
    "fabricAppId": "YOUR_FABRIC_APP_ID",           # From Telebirr admin
    "appSecret": "YOUR_APP_SECRET",               # From Telebirr admin  
    "merchantAppId": "YOUR_MERCHANT_APP_ID",       # From Telebirr admin
    "merchantCode": "YOUR_MERCHANT_CODE",         # From Telebirr admin
    
    # Public/Private key pair for RSA signatures
    "public_key": """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
YOUR_PUBLIC_KEY_FROM_TELEBIRR_ADMIN
-----END PUBLIC KEY-----
    """.strip(),
    
    "private_key": """
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
YOUR_PRIVATE_KEY_FROM_TELEBIRR_ADMIN
-----END PRIVATE KEY-----
    """.strip(),
    
    # URLs
    "notifyUrl": "https://your-domain.com/api/payments/telebirr/notify",
    "redirectUrl": "https://your-domain.com/payments/return",
    
    # Business details
    "receive_name": "Your Company Name",
    "timeout_express": "30",  # Payment timeout in minutes
    
    # Environment
    "test_mode": True,  # Set to False for production
    "base_url": "https://mmpay.trade.pay"  # Official Telebirr API domain
}

# Environment variables for production
TELEBIRR_ENV_VARS = {
    "TELEBIRR_FABRIC_APP_ID": "fabricAppId",
    "TELEBIRR_APP_SECRET": "appSecret", 
    "TELEBIRR_MERCHANT_APP_ID": "merchantAppId",
    "TELEBIRR_MERCHANT_CODE": "merchantCode",
    "TELEBIRR_PUBLIC_KEY": "public_key",
    "TELEBIRR_PRIVATE_KEY": "private_key",
    "TELEBIRR_NOTIFY_URL": "notifyUrl",
    "TELEBIRR_REDIRECT_URL": "redirectUrl",
    "TELEBIRR_RECEIVE_NAME": "receive_name",
    "TELEBIRR_TIMEOUT_EXPRESS": "timeout_express",
    "TELEBIRR_TEST_MODE": "test_mode"
}

# How to use in settings extended.py
def get_telebirr_official_config():
    """Load Telebirr official configuration from environment."""
    import os
    
    return {
        "fabricAppId": os.getenv("TELEBIRR_FABRIC_APP_ID"),
        "appSecret": os.getenv("TELEBIRR_APP_SECRET"),
        "merchantAppId": os.getenv("TELEBIRR_MERCHANT_APP_ID"), 
        "merchantCode": os.getenv("TELEBIRR_MERCHANT_CODE"),
        "public_key": os.getenv("TELEBIRR_PUBLIC_KEY"),
        "private_key": os.getenv("TELEBIRR_PRIVATE_KEY"),
        "notifyUrl": os.getenv("TELEBIRR_NOTIFY_URL", "https://your-domain.com/api/payments/telebirr/notify"),
        "redirectUrl": os.getenv("TELEBIRR_REDIRECT_URL", "https://your-domain.com/payments/return"),
        "receive_name": os.getenv("TELEBIRR_RECEIVE_NAME", "Your Company Name"),
        "timeout_express": os.getenv("TELEBIRR_TIMEOUT_EXPRESS", "30"),
        "test_mode": os.getenv("TELEBIRR_TEST_MODE", "true").lower() == "true",
        "base_url": os.getenv("TELEBIRR_BASE_URL", "https://mmpay.trade.pay")
    }

# Example .env file configuration
"""
# Telebirr Official Configuration
TELEBIRR_FABRIC_APP_ID=your_fabric_app_id
TELEBIRR_APP_SECRET=your_app_secret
TELEBIRR_MERCHANT_APP_ID=your_merchant_app_id
TELEBIRR_MERCHANT_CODE=your_merchant_code
TELEBIRR_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----
TELEBIRR_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----
TELEBIRR_NOTIFY_URL=https://your-domain.com/api/payments/telebirr/notify
TELEBIRR_REDIRECT_URL=https://your-domain.com/payments/return
TELEBIRR_RECEIVE_NAME=Your Company Name
TELEBIRR_TIMEOUT_EXPRESS=30
TELEBIRR_TEST_MODE=true
TELEBIRR_BASE_URL=https://mmpay.trade.pay
"""

# Key differences from previous implementations:
"""
1. CREDENTIALS:
   - Uses fabricAppId, appSecret, merchantAppId, merchantCode
   - NOT app_id, app_secret, merchant_code (different naming)

2. ENCRYPTION:
   - Requires RSA public/private key pair for signatures
   - NOT HMAC-SHA256 with app_secret

3. API ENDPOINTS:
   - Uses mmpay.trade.pay domain
   - NOT api.telebirr.et

4. REQUEST FORMAT:
   - Different field names and structure
   - Requires nonce and specific timestamp format

5. RESPONSE FORMAT:
   - checkoutUrl in data.checkoutUrl
   - Different error handling

6. CALLBACKS:
   - Encrypted payload requiring decryption
   - Different callback structure
"""

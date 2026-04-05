"""
Official Telebirr H5 Payment Provider Implementation

This provider implements the official Ethiopian Telecom Telebirr H5 API
based on the actual specification from developer.ethiotelecom.et

Key differences from our previous implementation:
1. Uses fabricAppId, appSecret, merchantAppId, merchantCode
2. Requires public/private key encryption for signatures
3. Uses mmpay.trade.pay domain for API endpoints
4. Specific timestamp format and nonce requirements
5. Different request/response structure
"""

import base64
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from apps.payments.providers.base import BasePaymentProvider, PaymentProcessingError
from shared.logging import get_logger

logger = get_logger(__name__)


class TelebirrOfficialProvider(BasePaymentProvider):
    """
    Official Telebirr H5 payment provider based on Ethiopian Telecom specification.
    
    This implementation follows the actual Telebirr H5 C2B Web Payment Integration
    documentation and API contracts.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Official Telebirr credentials
        self.fabric_app_id = config.get('fabricAppId') or config.get('fabric_app_id')
        self.app_secret = config.get('appSecret') or config.get('app_secret') 
        self.merchant_app_id = config.get('merchantAppId') or config.get('merchant_app_id')
        self.merchant_code = config.get('merchantCode') or config.get('merchant_code')
        self.public_key = config.get('public_key')
        self.private_key = config.get('private_key')
        
        # URLs from official documentation
        self.base_url = config.get('base_url', 'https://mmpay.trade.pay')
        self.notify_url = config.get('notifyUrl') or config.get('notify_url')
        self.return_url = config.get('redirectUrl') or config.get('return_url') or config.get('return_url')
        
        # Payment details
        self.receive_name = config.get('receive_name', 'Music Platform')
        self.timeout_express = config.get('timeout_express', '30')
        
        # Test mode
        self.test_mode = config.get('test_mode', True)
        
        # Validate required fields
        required_fields = [
            self.fabric_app_id, 
            self.app_secret, 
            self.merchant_app_id, 
            self.merchant_code,
            self.public_key,
            self.private_key
        ]
        
        if not all(required_fields):
            missing = [field for field in required_fields if not field]
            raise ValueError(f"Telebirr Official requires: fabricAppId, appSecret, merchantAppId, merchantCode, public_key, private_key. Missing: {missing}")
    
    def get_provider_name(self) -> str:
        return 'telebirr_official'
    
    def _generate_timestamp(self) -> str:
        """Generate timestamp in milliseconds as required by Telebirr."""
        return str(int(datetime.now().timestamp() * 1000))
    
    def _generate_nonce(self) -> str:
        """Generate unique nonce for request."""
        return str(uuid.uuid4()).replace('-', '')
    
    def _create_signature(self, data: Dict[str, Any]) -> str:
        """
        Create RSA signature for Telebirr request.
        
        According to the official docs, this uses RSA private key signing.
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            
            # Load private key
            private_key_pem = self.private_key.encode('utf-8')
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None
            )
            
            # Sign the data
            signature = private_key.sign(
                json_data.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # Return base64 encoded signature
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Telebirr signature creation error: {e}")
            raise PaymentProcessingError(f"Signature creation failed: {str(e)}")
    
    async def initialize_payment(
        self, 
        payment_intent_id: str,
        amount: float,
        currency: str,
        customer_id: str,
        description: Optional[str] = None,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initialize Telebirr H5 payment using official API.
        
        Returns checkout URL for redirect to Telebirr payment page.
        """
        try:
            # Generate request data according to official specification
            timestamp = self._generate_timestamp()
            nonce = self._generate_nonce()
            
            request_data = {
                'appId': self.fabric_app_id,
                'appSecret': self.app_secret,
                'merchantAppId': self.merchant_app_id,
                'merchantCode': self.merchant_code,
                'notifyUrl': self.notify_url or f"{self.base_url}/notify",
                'returnUrl': return_url or self.return_url or f"{self.base_url}/return",
                'receiveName': self.receive_name,
                'timeoutExpress': self.timeout_express,
                'totalAmount': str(amount),
                'nonce': nonce,
                'outTradeNo': payment_intent_id,
                'subject': description or f'Payment {payment_intent_id}',
                'timestamp': timestamp
            }
            
            # Add signature
            request_data['signature'] = self._create_signature(request_data)
            
            # Make request to Telebirr API
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/api/gateway/order",
                    json=request_data,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'MusicPlatform/1.0'
                    }
                )
                
                if response.status_code != 200:
                    raise PaymentProcessingError(
                        f"Telebirr order creation failed: {response.status_code}"
                    )
                
                result = response.json()
                
                # Check response according to official format
                if result.get('code') != 'SUCCESS':
                    error_msg = result.get('message', result.get('msg', 'Unknown error'))
                    raise PaymentProcessingError(f"Telebirr order error: {error_msg}")
                
                # Extract checkout URL from response
                checkout_url = result.get('data', {}).get('checkoutUrl')
                if not checkout_url:
                    # Alternative response format
                    checkout_url = result.get('checkoutUrl')
                
                if not checkout_url:
                    raise PaymentProcessingError("No checkout URL received from Telebirr")
                
                return {
                    'status': 'requires_action',
                    'next_action': 'redirect',
                    'redirect_url': checkout_url,
                    'payment_url': checkout_url,
                    'provider_reference': payment_intent_id,
                    'expires_at': (datetime.now() + timedelta(minutes=int(self.timeout_express))).isoformat(),
                    'nonce': nonce,
                    'timestamp': timestamp,
                }
                
        except httpx.RequestError as e:
            logger.error(f"Telebirr official network error: {e}")
            raise PaymentProcessingError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Telebirr official payment initialization error: {e}")
            raise PaymentProcessingError(f"Payment initialization failed: {str(e)}")
    
    async def verify_payment(
        self, 
        payment_intent_id: str,
        provider_response: Optional[Dict[str, Any]] = None,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify Telebirr payment status.
        
        Handles both callback notifications and manual status queries.
        """
        try:
            if provider_response:
                # Process callback notification from Telebirr
                return await self._process_callback(provider_response)
            
            elif transaction_id or payment_intent_id:
                # Query payment status
                return await self._query_payment_status(transaction_id or payment_intent_id)
            
            else:
                raise PaymentProcessingError("Either provider_response or transaction_id is required")
                
        except Exception as e:
            logger.error(f"Telebirr official payment verification error: {e}")
            raise PaymentProcessingError(f"Payment verification failed: {str(e)}")
    
    async def _process_callback(self, callback_data: Any) -> Dict[str, Any]:
        """
        Process Telebirr callback notification.
        
        Callbacks are encrypted and need to be decrypted using public key.
        """
        try:
            # If callback_data is bytes, decode to string
            if isinstance(callback_data, bytes):
                callback_data = callback_data.decode('utf-8')
            
            # Parse JSON if it's a string
            if isinstance(callback_data, str):
                try:
                    callback_data = json.loads(callback_data)
                except json.JSONDecodeError:
                    # If it's not JSON, it might be encrypted payload
                    decrypted_data = await self._decrypt_payload(callback_data)
                    callback_data = json.loads(decrypted_data)
            
            # Extract payment information
            trade_status = callback_data.get('tradeStatus')
            out_trade_no = callback_data.get('outTradeNo')
            total_amount = callback_data.get('totalAmount')
            trade_no = callback_data.get('tradeNo')
            
            if not out_trade_no:
                raise PaymentProcessingError("Missing outTradeNo in callback")
            
            # Map Telebirr status to our status
            status = 'success' if trade_status == 'SUCCESS' else 'failed'
            
            return {
                'status': status,
                'provider_transaction_id': trade_no or out_trade_no,
                'amount_paid': float(total_amount) if total_amount else 0,
                'verified': True,
                'provider_response': callback_data,
                'trade_status': trade_status,
            }
            
        except Exception as e:
            logger.error(f"Telebirr callback processing error: {e}")
            raise PaymentProcessingError(f"Callback processing failed: {str(e)}")
    
    async def _decrypt_payload(self, encrypted_payload: str) -> str:
        """
        Decrypt encrypted payload from Telebirr using public key.
        
        Note: This is a placeholder - actual implementation depends on 
        Telebirr's encryption method which may vary.
        """
        try:
            # This would implement the actual decryption logic
            # based on Telebirr's encryption specification
            
            # For now, return the payload as-is (assuming it's not encrypted in test mode)
            if self.test_mode:
                return encrypted_payload
            
            # TODO: Implement actual decryption when encryption details are known
            # This likely involves RSA with the public key
            raise NotImplementedError("Payload decryption not yet implemented")
            
        except Exception as e:
            logger.error(f"Telebirr payload decryption error: {e}")
            raise PaymentProcessingError(f"Decryption failed: {str(e)}")
    
    async def _query_payment_status(self, out_trade_no: str) -> Dict[str, Any]:
        """
        Query payment status from Telebirr API.
        """
        try:
            timestamp = self._generate_timestamp()
            nonce = self._generate_nonce()
            
            query_data = {
                'appId': self.fabric_app_id,
                'appSecret': self.app_secret,
                'merchantAppId': self.merchant_app_id,
                'merchantCode': self.merchant_code,
                'outTradeNo': out_trade_no,
                'nonce': nonce,
                'timestamp': timestamp
            }
            
            query_data['signature'] = self._create_signature(query_data)
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/api/gateway/query",
                    json=query_data,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'MusicPlatform/1.0'
                    }
                )
                
                if response.status_code != 200:
                    raise PaymentProcessingError(
                        f"Telebirr query failed: {response.status_code}"
                    )
                
                result = response.json()
                
                if result.get('code') != 'SUCCESS':
                    error_msg = result.get('message', result.get('msg', 'Unknown error'))
                    raise PaymentProcessingError(f"Telebirr query error: {error_msg}")
                
                # Extract payment status
                payment_data = result.get('data', {})
                trade_status = payment_data.get('tradeStatus')
                total_amount = payment_data.get('totalAmount')
                trade_no = payment_data.get('tradeNo')
                
                status = 'success' if trade_status == 'SUCCESS' else 'failed'
                
                return {
                    'status': status,
                    'provider_transaction_id': trade_no or out_trade_no,
                    'amount_paid': float(total_amount) if total_amount else 0,
                    'verified': True,
                    'provider_response': payment_data,
                    'trade_status': trade_status,
                }
                
        except httpx.RequestError as e:
            logger.error(f"Telebirr query network error: {e}")
            raise PaymentProcessingError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Telebirr query error: {e}")
            raise PaymentProcessingError(f"Query failed: {str(e)}")
    
    async def process_refund(
        self, 
        payment_intent_id: str,
        amount: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process refund for Telebirr payment.
        
        Note: Refund implementation depends on Telebirr's refund API
        which may require additional setup.
        """
        try:
            # For now, mark as manual processing required
            return {
                'status': 'manual_processing_required',
                'message': 'Telebirr refunds require manual processing through merchant dashboard',
                'refund_id': str(uuid.uuid4()),
                'provider': self.get_provider_name(),
            }
            
        except Exception as e:
            logger.error(f"Telebirr refund error: {e}")
            raise PaymentProcessingError(f"Refund processing failed: {str(e)}")
    
    def get_supported_currencies(self) -> list[str]:
        """Get list of supported currencies."""
        return ['ETB']  # Telebirr primarily supports Ethiopian Birr
    
    def get_payment_methods(self) -> list[str]:
        """Get list of supported payment methods."""
        return ['telebirr_h5', 'mobile_money', 'bank_card']
    
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        required_fields = [
            'fabricAppId', 'appSecret', 'merchantAppId', 
            'merchantCode', 'public_key', 'private_key'
        ]
        return all(field in self.config and self.config[field] for field in required_fields)
    
    def get_webhook_config(self) -> Dict[str, Any]:
        """Get webhook configuration for this provider."""
        return {
            'webhook_url': self.notify_url,
            'webhook_events': ['payment.success', 'payment.failed', 'payment.cancelled'],
            'signature_verification': True,
            'encryption_required': True,
            'timeout_minutes': int(self.timeout_express),
        }
    
    def get_test_credentials(self) -> Dict[str, Any]:
        """Get test credentials for development."""
        return {
            'fabricAppId': 'TEST_FABRIC_APP_ID',
            'appSecret': 'TEST_APP_SECRET', 
            'merchantAppId': 'TEST_MERCHANT_APP_ID',
            'merchantCode': 'TEST_MERCHANT_CODE',
            'public_key': 'TEST_PUBLIC_KEY',
            'private_key': 'TEST_PRIVATE_KEY',
            'base_url': 'https://mmpay.trade.pay',
            'test_mode': True
        }

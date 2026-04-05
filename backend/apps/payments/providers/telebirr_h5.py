"""
Telebirr H5 Payment Provider Implementation

This provider implements the Telebirr H5 (web-based) payment flow
with proper redirect handling and callback verification.
"""

import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx

from apps.payments.providers.base import BasePaymentProvider, PaymentProcessingError
from shared.logging import get_logger

logger = get_logger(__name__)


class TelebirrH5Provider(BasePaymentProvider):
    """
    Telebirr H5 payment provider for web-based checkout.
    
    This implementation follows the Telebirr H5 documentation:
    1. Create payment order
    2. Redirect user to Telebirr checkout
    3. Handle callback verification
    4. Query payment status
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://api.telebirr.et')
        self.app_id = config.get('app_id')
        self.app_secret = config.get('app_secret')
        self.merchant_code = config.get('merchant_code')
        self.short_code = config.get('short_code')
        self.test_mode = config.get('test_mode', True)
        
        if not all([self.app_id, self.app_secret, self.merchant_code]):
            raise ValueError("Telebirr H5 requires app_id, app_secret, and merchant_code")
    
    def get_provider_name(self) -> str:
        return 'telebirr_h5'
    
    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """Generate HMAC-SHA256 signature for Telebirr API."""
        # Sort keys and create signature string
        sorted_keys = sorted(data.keys())
        sign_string = '&'.join([f"{key}={data[key]}" for key in sorted_keys])
        
        # Add app secret
        sign_string += f"&appSecret={self.app_secret}"
        
        # Generate HMAC-SHA256
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
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
        Initialize Telebirr H5 payment.
        
        Returns redirect URL for user checkout.
        """
        try:
            # Prepare payment order data
            order_data = {
                'appId': self.app_id,
                'merchantCode': self.merchant_code,
                'orderNo': payment_intent_id,
                'amount': int(amount * 100),  # Convert to cents
                'currency': currency,
                'notifyUrl': f"{self.base_url}/webhook/telebirr",
                'returnUrl': return_url or f"{self.base_url}/payment/return",
                'cancelUrl': cancel_url or f"{self.base_url}/payment/cancel",
                'subject': description or f'Payment {payment_intent_id}',
                'timestamp': str(int(datetime.now().timestamp() * 1000)),
            }
            
            # Add signature
            order_data['sign'] = self._generate_signature(order_data)
            
            # Create payment order
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/payment/order",
                    json=order_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code != 200:
                    raise PaymentProcessingError(
                        f"Telebirr order creation failed: {response.status_code}"
                    )
                
                result = response.json()
                
                if result.get('code') != 'SUCCESS':
                    raise PaymentProcessingError(
                        f"Telebirr order error: {result.get('message', 'Unknown error')}"
                    )
                
                # Extract checkout URL
                checkout_url = result.get('data', {}).get('checkoutUrl')
                if not checkout_url:
                    raise PaymentProcessingError("No checkout URL received from Telebirr")
                
                return {
                    'status': 'requires_action',
                    'next_action': 'redirect',
                    'redirect_url': checkout_url,
                    'payment_url': checkout_url,
                    'provider_reference': result.get('data', {}).get('orderNo'),
                    'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
                }
                
        except httpx.RequestError as e:
            logger.error(f"Telebirr H5 network error: {e}")
            raise PaymentProcessingError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Telebirr H5 payment initialization error: {e}")
            raise PaymentProcessingError(f"Payment initialization failed: {str(e)}")
    
    async def verify_payment(
        self, 
        payment_intent_id: str,
        provider_response: Optional[Dict[str, Any]] = None,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify Telebirr H5 payment status.
        
        Can be called with callback data or by querying payment status.
        """
        try:
            if provider_response:
                # Verify callback signature
                if not self._verify_callback_signature(provider_response):
                    raise PaymentProcessingError("Invalid Telebirr callback signature")
                
                # Extract payment status from callback
                order_no = provider_response.get('orderNo')
                status = provider_response.get('status')
                amount = provider_response.get('amount')
                
                if not order_no:
                    raise PaymentProcessingError("Missing order number in callback")
                
                return {
                    'status': 'success' if status == 'SUCCESS' else 'failed',
                    'provider_transaction_id': order_no,
                    'amount_paid': float(amount) / 100 if amount else 0,
                    'verified': True,
                    'provider_response': provider_response,
                }
            
            elif transaction_id:
                # Query payment status directly
                return await self._query_payment_status(transaction_id)
            
            else:
                # Query by payment intent ID
                return await self._query_payment_status(payment_intent_id)
                
        except Exception as e:
            logger.error(f"Telebirr H5 payment verification error: {e}")
            raise PaymentProcessingError(f"Payment verification failed: {str(e)}")
    
    async def _query_payment_status(self, order_no: str) -> Dict[str, Any]:
        """Query payment status from Telebirr API."""
        try:
            query_data = {
                'appId': self.app_id,
                'merchantCode': self.merchant_code,
                'orderNo': order_no,
                'timestamp': str(int(datetime.now().timestamp() * 1000)),
            }
            
            query_data['sign'] = self._generate_signature(query_data)
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/payment/query",
                    json=query_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code != 200:
                    raise PaymentProcessingError(
                        f"Telebirr query failed: {response.status_code}"
                    )
                
                result = response.json()
                
                if result.get('code') != 'SUCCESS':
                    raise PaymentProcessingError(
                        f"Telebirr query error: {result.get('message', 'Unknown error')}"
                    )
                
                payment_data = result.get('data', {})
                status = payment_data.get('status')
                
                return {
                    'status': 'success' if status == 'SUCCESS' else 'failed',
                    'provider_transaction_id': order_no,
                    'amount_paid': float(payment_data.get('amount', 0)) / 100,
                    'verified': True,
                    'provider_response': payment_data,
                }
                
        except httpx.RequestError as e:
            logger.error(f"Telebirr H5 query network error: {e}")
            raise PaymentProcessingError(f"Network error: {str(e)}")
    
    def _verify_callback_signature(self, callback_data: Dict[str, Any]) -> bool:
        """Verify Telebirr callback signature."""
        try:
            received_sign = callback_data.get('sign')
            if not received_sign:
                return False
            
            # Create signature from callback data
            sign_data = callback_data.copy()
            sign_data.pop('sign', None)  # Remove signature from data
            
            expected_sign = self._generate_signature(sign_data)
            
            # Constant-time comparison
            return hmac.compare_digest(received_sign, expected_sign)
            
        except Exception as e:
            logger.error(f"Telebirr callback signature verification error: {e}")
            return False
    
    async def process_refund(
        self, 
        payment_intent_id: str,
        amount: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process refund for Telebirr H5 payment.
        
        Note: Telebirr H5 refunds may require manual processing
        through their merchant dashboard.
        """
        try:
            # For now, mark as manual processing required
            return {
                'status': 'manual_processing_required',
                'message': 'Telebirr H5 refunds require manual processing through merchant dashboard',
                'refund_id': str(uuid.uuid4()),
                'provider': self.get_provider_name(),
            }
            
        except Exception as e:
            logger.error(f"Telebirr H5 refund error: {e}")
            raise PaymentProcessingError(f"Refund processing failed: {str(e)}")
    
    def get_supported_currencies(self) -> list[str]:
        """Get list of supported currencies."""
        return ['ETB']  # Telebirr primarily supports Ethiopian Birr
    
    def get_payment_methods(self) -> list[str]:
        """Get list of supported payment methods."""
        return ['telebirr_h5', 'mobile_money', 'bank_card']
    
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        required_fields = ['app_id', 'app_secret', 'merchant_code']
        return all(field in self.config and self.config[field] for field in required_fields)
    
    def get_webhook_config(self) -> Dict[str, Any]:
        """Get webhook configuration for this provider."""
        return {
            'webhook_url': f"{self.base_url}/webhook/telebirr",
            'webhook_events': ['payment.success', 'payment.failed', 'payment.cancelled'],
            'signature_header': 'X-Telebirr-Signature',
            'signature_verification': True,
        }

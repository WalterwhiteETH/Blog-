"""
M-Pesa Payment Provider Implementation

This provider implements Safaricom M-Pesa payment integration
for Ethiopian market with proper auth and transaction handling.
"""

import base64
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

from apps.payments.providers.base import BasePaymentProvider, PaymentProcessingError
from shared.logging import get_logger

logger = get_logger(__name__)


class MpesaProvider(BasePaymentProvider):
    """
    M-Pesa payment provider for Ethiopian market.
    
    This implementation follows Safaricom M-Pesa API:
    1. Authentication and token generation
    2. STK Push for customer payment
    3. Transaction status query
    4. Callback handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://api.safaricom.et')
        self.consumer_key = config.get('consumer_key')
        self.consumer_secret = config.get('consumer_secret')
        self.business_short_code = config.get('business_short_code')
        self.passkey = config.get('passkey')
        self.test_mode = config.get('test_mode', True)
        
        # Cache for access token
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
        if not all([self.consumer_key, self.consumer_secret, self.business_short_code, self.passkey]):
            raise ValueError("M-Pesa requires consumer_key, consumer_secret, business_short_code, and passkey")
    
    def get_provider_name(self) -> str:
        return 'mpesa'
    
    async def _get_access_token(self) -> str:
        """Get or refresh M-Pesa access token."""
        # Check if cached token is still valid
        if (self._access_token and 
            self._token_expires_at and 
            datetime.now() < self._token_expires_at):
            return self._access_token
        
        try:
            # Create basic auth credentials
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
                    headers={
                        'Authorization': f'Basic {encoded_credentials}',
                        'Content-Type': 'application/json'
                    }
                )
                
                if response.status_code != 200:
                    raise PaymentProcessingError(
                        f"M-Pesa authentication failed: {response.status_code}"
                    )
                
                result = response.json()
                access_token = result.get('access_token')
                expires_in = result.get('expires_in', 3600)
                
                if not access_token:
                    raise PaymentProcessingError("No access token received from M-Pesa")
                
                # Cache token
                self._access_token = access_token
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 min early
                
                return access_token
                
        except httpx.RequestError as e:
            logger.error(f"M-Pesa auth network error: {e}")
            raise PaymentProcessingError(f"Authentication network error: {str(e)}")
        except Exception as e:
            logger.error(f"M-Pesa authentication error: {e}")
            raise PaymentProcessingError(f"Authentication failed: {str(e)}")
    
    def _generate_password(self, timestamp: str) -> str:
        """Generate M-Pesa STK push password."""
        password_string = f"{self.business_short_code}{self.passkey}{timestamp}"
        return base64.b64encode(password_string.encode()).decode()
    
    async def initialize_payment(
        self, 
        payment_intent_id: str,
        amount: float,
        currency: str,
        customer_id: str,
        phone_number: Optional[str] = None,
        description: Optional[str] = None,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initialize M-Pesa STK Push payment.
        
        Returns STK push request status and checkout request ID.
        """
        try:
            access_token = await self._get_access_token()
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password(timestamp)
            
            # Prepare STK push request
            stk_push_data = {
                'BusinessShortCode': self.business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': int(amount),  # M-Pesa expects integer amount
                'PartyA': phone_number or customer_id,  # Customer phone number
                'PartyB': self.business_short_code,
                'PhoneNumber': phone_number or customer_id,
                'CallBackURL': f"{self.base_url}/mpesa/callback",
                'AccountReference': payment_intent_id,
                'TransactionDesc': description or f'Payment {payment_intent_id}',
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                    json=stk_push_data,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                )
                
                if response.status_code != 200:
                    raise PaymentProcessingError(
                        f"M-Pesa STK push failed: {response.status_code}"
                    )
                
                result = response.json()
                
                if result.get('ResponseCode') != '0':
                    error_message = result.get('errorMessage', result.get('ResponseDescription', 'Unknown error'))
                    raise PaymentProcessingError(f"M-Pesa STK push error: {error_message}")
                
                checkout_request_id = result.get('CheckoutRequestID')
                merchant_request_id = result.get('MerchantRequestID')
                customer_message = result.get('CustomerMessage', 'Please complete payment on your phone')
                
                return {
                    'status': 'requires_action',
                    'next_action': 'stk_push',
                    'checkout_request_id': checkout_request_id,
                    'merchant_request_id': merchant_request_id,
                    'customer_message': customer_message,
                    'phone_number': phone_number or customer_id,
                    'provider_reference': checkout_request_id,
                    'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat(),  # STK push expires in 10 minutes
                }
                
        except httpx.RequestError as e:
            logger.error(f"M-Pesa STK push network error: {e}")
            raise PaymentProcessingError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"M-Pesa payment initialization error: {e}")
            raise PaymentProcessingError(f"Payment initialization failed: {str(e)}")
    
    async def verify_payment(
        self, 
        payment_intent_id: str,
        provider_response: Optional[Dict[str, Any]] = None,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify M-Pesa payment status.
        
        Can be called with callback data or by querying transaction status.
        """
        try:
            if provider_response:
                # Process callback data
                return self._process_callback(provider_response)
            
            elif transaction_id:
                # Query transaction status
                return await self._query_transaction_status(transaction_id)
            
            else:
                raise PaymentProcessingError("Either provider_response or transaction_id is required")
                
        except Exception as e:
            logger.error(f"M-Pesa payment verification error: {e}")
            raise PaymentProcessingError(f"Payment verification failed: {str(e)}")
    
    def _process_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process M-Pesa callback data."""
        try:
            # Extract result from callback
            result = callback_data.get('Body', {}).get('stkCallback', {})
            
            result_code = result.get('ResultCode')
            result_desc = result.get('ResultDesc')
            merchant_request_id = result.get('MerchantRequestID')
            checkout_request_id = result.get('CheckoutRequestID')
            
            if result_code == '0':
                # Payment successful
                callback_metadata = result.get('CallbackMetadata', {}).get('Item', [])
                
                # Extract payment details
                amount = 0
                mpesa_receipt_number = None
                transaction_date = None
                phone_number = None
                
                for item in callback_metadata:
                    name = item.get('Name')
                    value = item.get('Value')
                    
                    if name == 'Amount':
                        amount = value
                    elif name == 'MpesaReceiptNumber':
                        mpesa_receipt_number = value
                    elif name == 'TransactionDate':
                        transaction_date = value
                    elif name == 'PhoneNumber':
                        phone_number = value
                
                return {
                    'status': 'success',
                    'provider_transaction_id': mpesa_receipt_number or checkout_request_id,
                    'amount_paid': float(amount),
                    'verified': True,
                    'provider_response': callback_data,
                    'transaction_date': transaction_date,
                    'phone_number': phone_number,
                }
            else:
                # Payment failed
                return {
                    'status': 'failed',
                    'provider_transaction_id': checkout_request_id,
                    'amount_paid': 0,
                    'verified': True,
                    'provider_response': callback_data,
                    'error_message': result_desc,
                }
                
        except Exception as e:
            logger.error(f"M-Pesa callback processing error: {e}")
            raise PaymentProcessingError(f"Callback processing failed: {str(e)}")
    
    async def _query_transaction_status(self, checkout_request_id: str) -> Dict[str, Any]:
        """Query M-Pesa transaction status."""
        try:
            access_token = await self._get_access_token()
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password(timestamp)
            
            # Prepare status query request
            status_data = {
                'BusinessShortCode': self.business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': checkout_request_id,
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/mpesa/stkpushquery/v1/query",
                    json=status_data,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                )
                
                if response.status_code != 200:
                    raise PaymentProcessingError(
                        f"M-Pesa status query failed: {response.status_code}"
                    )
                
                result = response.json()
                
                if result.get('ResponseCode') != '0':
                    error_message = result.get('errorMessage', result.get('ResponseDescription', 'Unknown error'))
                    raise PaymentProcessingError(f"M-Pesa status query error: {error_message}")
                
                # Extract status information
                callback_metadata = result.get('CallbackMetadata', {}).get('Item', [])
                
                result_code = None
                amount = 0
                mpesa_receipt_number = None
                
                for item in callback_metadata:
                    name = item.get('Name')
                    value = item.get('Value')
                    
                    if name == 'ResultCode':
                        result_code = value
                    elif name == 'Amount':
                        amount = value
                    elif name == 'MpesaReceiptNumber':
                        mpesa_receipt_number = value
                
                return {
                    'status': 'success' if result_code == '0' else 'failed',
                    'provider_transaction_id': mpesa_receipt_number or checkout_request_id,
                    'amount_paid': float(amount),
                    'verified': True,
                    'provider_response': result,
                }
                
        except httpx.RequestError as e:
            logger.error(f"M-Pesa status query network error: {e}")
            raise PaymentProcessingError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"M-Pesa status query error: {e}")
            raise PaymentProcessingError(f"Status query failed: {str(e)}")
    
    async def process_refund(
        self, 
        payment_intent_id: str,
        amount: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process refund for M-Pesa payment.
        
        Note: M-Pesa refunds require business-level API access
        and may need manual approval.
        """
        try:
            # For now, mark as manual processing required
            return {
                'status': 'manual_processing_required',
                'message': 'M-Pesa refunds require business-level API access and manual approval',
                'refund_id': str(uuid.uuid4()),
                'provider': self.get_provider_name(),
            }
            
        except Exception as e:
            logger.error(f"M-Pesa refund error: {e}")
            raise PaymentProcessingError(f"Refund processing failed: {str(e)}")
    
    def get_supported_currencies(self) -> list[str]:
        """Get list of supported currencies."""
        return ['ETB', 'KES']  # Ethiopian Birr and Kenyan Shilling
    
    def get_payment_methods(self) -> list[str]:
        """Get list of supported payment methods."""
        return ['mpesa_stk_push', 'mobile_money']
    
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        required_fields = ['consumer_key', 'consumer_secret', 'business_short_code', 'passkey']
        return all(field in self.config and self.config[field] for field in required_fields)
    
    def get_webhook_config(self) -> Dict[str, Any]:
        """Get webhook configuration for this provider."""
        return {
            'webhook_url': f"{self.base_url}/mpesa/callback",
            'webhook_events': ['stk_push.success', 'stk_push.failed'],
            'signature_verification': False,  # M-Pesa doesn't use signatures
            'timeout_minutes': 10,  # STK push timeout
        }

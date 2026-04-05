import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from apps.payments.providers.manual_bank import ManualBankProvider
from apps.payments.schemas import PaymentProcessRequest

@pytest.fixture
def provider_config():
    return {
        'bank_name': 'Test Bank',
        'account_number': '123456789',
        'account_name': 'Test Account',
        'branch_name': 'Main Branch',
        'payment_deadline_hours': 24,
        'requires_receipt_upload': True,
        'auto_approve_threshold': 100
    }

@pytest.fixture
def manual_provider(provider_config):
    return ManualBankProvider(provider_config)

@pytest.mark.asyncio
async def test_initialize_payment_logic(manual_provider):
    # Create a mock payment intent
    mock_intent = MagicMock()
    mock_intent.id = 123
    mock_intent.amount = Decimal('50.00')
    mock_intent.currency = 'ETB'
    mock_intent.description = 'Subscription'
    
    request = PaymentProcessRequest(payment_intent=mock_intent)
    
    # Mock validation methods inherited from base class
    manual_provider.validate_amount = MagicMock()
    manual_provider.validate_currency = MagicMock()
    
    response = await manual_provider.initialize_payment(request)
    
    # Verify response structure
    assert response.next_action == 'manual_payment_required'
    assert response.transaction['can_auto_approve'] is True
    
    instructions = response.transaction['payment_instructions']
    assert instructions['bank_name'] == 'Test Bank'
    assert instructions['account_number'] == '123456789'
    assert instructions['amount'] == 50.0
    assert 'BNK123' in instructions['reference']

if __name__ == "__main__":
    pytest.main([__file__])
import pytest
from datetime import datetime

from banking_system.account import Account
from banking_system.exceptions import InvalidAmountError, InsufficientFundsError


class TestAccount:
    
    def test_account_creation_with_valid_data(self):
        account = Account("John Doe", 100.0)
        
        assert account.name == "John Doe"
        assert account.balance == 100.0
        assert len(account.account_id) == 8  # Short UUID
        assert isinstance(account.created_at, datetime)
    
    def test_account_creation_with_default_balance(self):
        account = Account("Jane Smith")
        
        assert account.name == "Jane Smith"
        assert account.balance == 0.0
    
    def test_account_creation_with_whitespace_name(self):
        account = Account("  Alice Johnson  ")
        
        assert account.name == "Alice Johnson"  # Should be stripped
    
    def test_account_creation_with_negative_balance_raises_error(self):
        with pytest.raises(InvalidAmountError) as exc_info:
            Account("Bob Wilson", -50.0)
        
        assert "Invalid amount" in str(exc_info.value)
        assert exc_info.value.amount == -50.0
    
    def test_deposit_valid_amount(self):
        account = Account("Carol Brown", 50.0)
        account.deposit(25.0)
        
        assert account.balance == 75.0
    
    def test_deposit_decimal_precision(self):
        account = Account("Dave Miller")
        account.deposit(0.01)  # One cent
        account.deposit(0.99)  # 99 cents
        
        assert account.balance == 1.0  # Should be exactly 1.00
    
    def test_deposit_zero_amount_raises_error(self):
        account = Account("Eve Davis")
        
        with pytest.raises(InvalidAmountError) as exc_info:
            account.deposit(0.0)
        
        assert exc_info.value.amount == 0.0
    
    def test_deposit_negative_amount_raises_error(self):
        account = Account("Frank Wilson")
        
        with pytest.raises(InvalidAmountError) as exc_info:
            account.deposit(-10.0)
        
        assert exc_info.value.amount == -10.0
    
    def test_withdraw_valid_amount(self):
        account = Account("Grace Lee", 100.0)
        account.withdraw(30.0)
        
        assert account.balance == 70.0
    
    def test_withdraw_entire_balance(self):
        account = Account("Henry Kim", 50.0)
        account.withdraw(50.0)
        
        assert account.balance == 0.0
    
    def test_withdraw_amount_exceeding_balance_raises_error(self):
        account = Account("Iris Chen", 25.0)
        
        with pytest.raises(InsufficientFundsError) as exc_info:
            account.withdraw(30.0)
        
        assert exc_info.value.account_id == account.account_id
        assert exc_info.value.requested_amount == 30.0
        assert exc_info.value.current_balance == 25.0
    
    def test_withdraw_zero_amount_raises_error(self):
        account = Account("Jack Thompson", 100.0)
        
        with pytest.raises(InvalidAmountError) as exc_info:
            account.withdraw(0.0)
        
        assert exc_info.value.amount == 0.0
    
    def test_withdraw_negative_amount_raises_error(self):
        account = Account("Kate Martinez", 100.0)
        
        with pytest.raises(InvalidAmountError) as exc_info:
            account.withdraw(-20.0)
        
        assert exc_info.value.amount == -20.0
    
    def test_multiple_transactions(self):
        account = Account("Luke Garcia", 100.0)
        
        account.deposit(50.0)   # 150.0
        account.withdraw(30.0)  # 120.0
        account.deposit(25.0)   # 145.0
        account.withdraw(45.0)  # 100.0
        
        assert account.balance == 100.0
    
    def test_to_dict_conversion(self):
        account = Account("Mary Rodriguez", 75.5)
        account_dict = account.to_dict()
        
        expected_keys = {'account_id', 'name', 'balance', 'created_at'}
        assert set(account_dict.keys()) == expected_keys
        assert account_dict['name'] == "Mary Rodriguez"
        assert account_dict['balance'] == 75.5
        assert account_dict['account_id'] == account.account_id
        assert isinstance(account_dict['created_at'], str)  # ISO format
    
    def test_from_dict_creation(self):
        account_data = {
            'account_id': 'test123',
            'name': 'Nathan Taylor',
            'balance': 200.0,
            'created_at': '2024-01-15T10:30:00'
        }
        
        account = Account.from_dict(account_data)
        
        assert account.account_id == 'test123'
        assert account.name == 'Nathan Taylor'
        assert account.balance == 200.0
        assert account.created_at == datetime.fromisoformat('2024-01-15T10:30:00')
    
    def test_account_string_representation(self):
        account = Account("Olivia Anderson", 150.0)
        
        str_repr = str(account)
        assert account.account_id in str_repr
        assert "Olivia Anderson" in str_repr
        assert "$150.00" in str_repr
        
        repr_str = repr(account)
        assert account.account_id in repr_str
        assert "Olivia Anderson" in repr_str
        assert "150.0" in repr_str
    
    def test_account_properties_are_readonly(self):
        account = Account("Paul Williams", 100.0)
        
        # These should not raise errors (properties are read-only by design)
        original_id = account.account_id
        original_name = account.name
        original_created_at = account.created_at
        
        # Verify properties return expected values
        assert account.account_id == original_id
        assert account.name == original_name
        assert account.created_at == original_created_at
    
    def test_decimal_rounding_precision(self):
        account = Account("Quinn Johnson")
        
        # Test deposits with many decimal places
        account.deposit(10.333333)  # Should round to 10.33
        account.deposit(5.666667)   # Should round to 5.67
        
        # Total should be 16.00 (10.33 + 5.67)
        assert account.balance == 16.0
    
    def test_large_amounts(self):
        account = Account("Rachel Davis", 1000000.0)  # One million
        
        account.deposit(500000.0)   # Half million
        account.withdraw(250000.0)  # Quarter million
        
        assert account.balance == 1250000.0
    
    def test_very_small_amounts(self):
        account = Account("Sam Wilson")
        
        account.deposit(0.01)  # One cent
        account.deposit(0.01)  # Another cent
        
        assert account.balance == 0.02 
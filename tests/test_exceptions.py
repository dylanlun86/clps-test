import pytest

from banking_system.exceptions import (
    BankingException,
    InsufficientFundsError,
    AccountNotFoundError,
    InvalidAmountError,
    DuplicateAccountError
)


class TestBankingExceptions:
    
    def test_banking_exception_base_class(self):
        message = "Test banking error"
        exception = BankingException(message)
        
        assert str(exception) == message
        assert exception.message == message
        assert isinstance(exception, Exception)
    
    def test_insufficient_funds_error(self):
        account_id = "test123"
        requested_amount = 150.0
        current_balance = 100.0
        
        exception = InsufficientFundsError(account_id, requested_amount, current_balance)
        
        # Test error message formatting
        expected_message = (
            f"Insufficient funds in account {account_id}. "
            f"Requested: ${requested_amount:.2f}, Available: ${current_balance:.2f}"
        )
        assert str(exception) == expected_message
        
        # Test attribute access
        assert exception.account_id == account_id
        assert exception.requested_amount == requested_amount
        assert exception.current_balance == current_balance
        
        # Test inheritance
        assert isinstance(exception, BankingException)
        assert isinstance(exception, Exception)
    
    def test_account_not_found_error(self):
        account_id = "nonexistent123"
        exception = AccountNotFoundError(account_id)
        
        expected_message = f"Account with ID '{account_id}' not found"
        assert str(exception) == expected_message
        assert exception.account_id == account_id
        
        # Test inheritance
        assert isinstance(exception, BankingException)
        assert isinstance(exception, Exception)
    
    def test_invalid_amount_error(self):
        amount = -25.50
        exception = InvalidAmountError(amount)
        
        expected_message = f"Invalid amount: ${amount:.2f}. Amount must be positive."
        assert str(exception) == expected_message
        assert exception.amount == amount
        
        # Test inheritance
        assert isinstance(exception, BankingException)
        assert isinstance(exception, Exception)
    
    def test_invalid_amount_error_zero(self):
        amount = 0.0
        exception = InvalidAmountError(amount)
        
        expected_message = f"Invalid amount: ${amount:.2f}. Amount must be positive."
        assert str(exception) == expected_message
        assert exception.amount == amount
    
    def test_duplicate_account_error(self):
        account_id = "duplicate123"
        exception = DuplicateAccountError(account_id)
        
        expected_message = f"Account with ID '{account_id}' already exists"
        assert str(exception) == expected_message
        assert exception.account_id == account_id
        
        # Test inheritance
        assert isinstance(exception, BankingException)
        assert isinstance(exception, Exception)
    
    def test_exception_chaining(self):
        # Test that specific exceptions can be caught as BankingException
        with pytest.raises(BankingException):
            raise InsufficientFundsError("test", 100.0, 50.0)
        
        with pytest.raises(BankingException):
            raise AccountNotFoundError("test")
        
        with pytest.raises(BankingException):
            raise InvalidAmountError(-10.0)
        
        with pytest.raises(BankingException):
            raise DuplicateAccountError("test")
    
    def test_exception_error_details(self):
        # Test InsufficientFundsError details
        insufficient_funds = InsufficientFundsError("acc123", 200.0, 150.0)
        assert "acc123" in str(insufficient_funds)
        assert "$200.00" in str(insufficient_funds)
        assert "$150.00" in str(insufficient_funds)
        assert "Insufficient funds" in str(insufficient_funds)
        
        # Test AccountNotFoundError details
        account_not_found = AccountNotFoundError("missing_account")
        assert "missing_account" in str(account_not_found)
        assert "not found" in str(account_not_found)
        
        # Test InvalidAmountError details
        invalid_amount = InvalidAmountError(-50.0)
        assert "$-50.00" in str(invalid_amount)
        assert "must be positive" in str(invalid_amount)
        
        # Test DuplicateAccountError details
        duplicate_account = DuplicateAccountError("existing_id")
        assert "existing_id" in str(duplicate_account)
        assert "already exists" in str(duplicate_account)
    
    def test_exception_formatting_edge_cases(self):
        # Test very large amounts
        large_amount_error = InvalidAmountError(-1000000.0)
        assert "$-1000000.00" in str(large_amount_error)
        
        # Test very small amounts
        small_amount_error = InsufficientFundsError("test", 0.01, 0.00)
        assert "$0.01" in str(small_amount_error)
        assert "$0.00" in str(small_amount_error)
        
        # Test empty account ID
        empty_id_error = AccountNotFoundError("")
        assert "''" in str(empty_id_error)
        
        # Test special characters in account ID
        special_id_error = AccountNotFoundError("test@account#123")
        assert "test@account#123" in str(special_id_error) 
import pytest
import os
import tempfile
import pandas as pd
from pathlib import Path

from banking_system.bank import Bank
from banking_system.exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidAmountError
)


class TestBank:

    @pytest.fixture
    def temp_csv_file(self):
        """Create a temporary CSV file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def bank(self, temp_csv_file):
        """Create a bank instance with temporary CSV file"""
        return Bank(temp_csv_file)
    
    def test_bank_initialization_empty(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        
        assert len(bank) == 0
        assert len(bank.list_accounts()) == 0
    
    def test_create_account_valid(self, bank):
        account_id = bank.create_account("John Doe", 100.0)
        
        assert len(account_id) == 8  # Short UUID
        assert account_id in bank
        assert bank.get_balance(account_id) == 100.0
    
    def test_create_account_default_balance(self, bank):
        account_id = bank.create_account("Jane Smith")
        
        assert bank.get_balance(account_id) == 0.0
    
    def test_create_account_empty_name_raises_error(self, bank):
        with pytest.raises(ValueError) as exc_info:
            bank.create_account("   ")  # Whitespace only
        
        assert "Account name cannot be empty" in str(exc_info.value)
    
    def test_get_account_existing(self, bank):
        account_id = bank.create_account("Bob Wilson", 50.0)
        account = bank.get_account(account_id)
        
        assert account.name == "Bob Wilson"
        assert account.balance == 50.0
    
    def test_get_account_nonexistent_raises_error(self, bank):
        with pytest.raises(AccountNotFoundError) as exc_info:
            bank.get_account("invalid123")
        
        assert exc_info.value.account_id == "invalid123"
    
    def test_deposit_valid_amount(self, bank):
        account_id = bank.create_account("Carol Brown", 50.0)
        bank.deposit(account_id, 25.0)
        
        assert bank.get_balance(account_id) == 75.0
    
    def test_withdraw_valid_amount(self, bank):
        account_id = bank.create_account("Dave Miller", 100.0)
        bank.withdraw(account_id, 30.0)
        
        assert bank.get_balance(account_id) == 70.0
    
    def test_transfer_valid_amount(self, bank):
        from_account = bank.create_account("Eve Davis", 100.0)
        to_account = bank.create_account("Frank Wilson", 50.0)
        
        bank.transfer(from_account, to_account, 25.0)
        
        assert bank.get_balance(from_account) == 75.0
        assert bank.get_balance(to_account) == 75.0
    
    def test_transfer_same_account_raises_error(self, bank):
        account_id = bank.create_account("Grace Lee", 100.0)
        
        with pytest.raises(ValueError) as exc_info:
            bank.transfer(account_id, account_id, 50.0)
        
        assert "Cannot transfer to the same account" in str(exc_info.value)
    
    def test_list_accounts(self, bank):
        id1 = bank.create_account("Henry Kim", 100.0)
        id2 = bank.create_account("Iris Chen", 200.0)
        
        accounts = bank.list_accounts()
        
        assert len(accounts) == 2
        account_names = [acc.name for acc in accounts]
        assert "Henry Kim" in account_names
        assert "Iris Chen" in account_names
    
    def test_bank_length(self, bank):
        assert len(bank) == 0
        
        bank.create_account("Jack Thompson", 100.0)
        assert len(bank) == 1
        
        bank.create_account("Kate Martinez", 200.0)
        assert len(bank) == 2
    
    def test_get_bank_summary_empty(self, bank):
        summary = bank.get_bank_summary()
        
        expected = {
            'total_accounts': 0,
            'total_balance': 0.0,
            'average_balance': 0.0,
            'min_balance': 0.0,
            'max_balance': 0.0
        }
        assert summary == expected
    
    def test_get_bank_summary_with_accounts(self, bank):
        bank.create_account("Luke Garcia", 100.0)
        bank.create_account("Mary Rodriguez", 200.0)
        bank.create_account("Nathan Taylor", 50.0)
        
        summary = bank.get_bank_summary()
        
        assert summary['total_accounts'] == 3
        assert summary['total_balance'] == 350.0
        assert summary['average_balance'] == pytest.approx(116.67, rel=1e-2)
        assert summary['min_balance'] == 50.0
        assert summary['max_balance'] == 200.0
    
    def test_bank_contains_operator(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        account_id = bank.create_account("Test User", 100.0)
        
        assert account_id in bank
        assert "nonexistent" not in bank
    
    def test_bank_len_operator(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        
        assert len(bank) == 0
        
        bank.create_account("User 1", 100.0)
        assert len(bank) == 1
        
        bank.create_account("User 2", 200.0)
        assert len(bank) == 2
    
    def test_auto_save_after_operations(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        account_id = bank.create_account("Auto Save Test", 100.0)
        
        # Verify account creation was saved
        bank2 = Bank(temp_csv_file)
        assert account_id in bank2
        
        # Test deposit auto-save
        bank.deposit(account_id, 50.0)
        bank3 = Bank(temp_csv_file)
        assert bank3.get_balance(account_id) == 150.0
        
        # Test withdrawal auto-save
        bank.withdraw(account_id, 25.0)
        bank4 = Bank(temp_csv_file)
        assert bank4.get_balance(account_id) == 125.0
    
    def test_transfer_atomicity(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        account1_id = bank.create_account("Account 1", 100.0)
        account2_id = bank.create_account("Account 2", 50.0)
        
        # Test successful transfer
        bank.transfer(account1_id, account2_id, 30.0)
        assert bank.get_balance(account1_id) == 70.0
        assert bank.get_balance(account2_id) == 80.0
        
        # Verify the transfer was saved
        bank2 = Bank(temp_csv_file)
        assert bank2.get_balance(account1_id) == 70.0
        assert bank2.get_balance(account2_id) == 80.0
    
    def test_save_to_csv(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        
        account1_id = bank.create_account("Wendy Chen", 100.0)
        account2_id = bank.create_account("Xavier Garcia", 250.0)
        
        # Verify CSV file was created
        assert os.path.exists(temp_csv_file)
        
        # Verify CSV content
        df = pd.read_csv(temp_csv_file)
        assert len(df) == 2
        assert set(df['account_id'].tolist()) == {account1_id, account2_id}
        assert 'Wendy Chen' in df['name'].tolist()
        assert 'Xavier Garcia' in df['name'].tolist()
    
    def test_load_from_csv_existing_file(self, temp_csv_file):
        # Create initial bank and save data
        bank1 = Bank(temp_csv_file)
        account1_id = bank1.create_account("Yuki Tanaka", 300.0)
        account2_id = bank1.create_account("Zoe Anderson", 175.0)
        
        # Create new bank instance and verify data is loaded
        bank2 = Bank(temp_csv_file)
        
        assert len(bank2) == 2
        assert account1_id in bank2
        assert account2_id in bank2
        
        account1 = bank2.get_account(account1_id)
        account2 = bank2.get_account(account2_id)
        
        assert account1.name == "Yuki Tanaka"
        assert account1.balance == 300.0
        assert account2.name == "Zoe Anderson"
        assert account2.balance == 175.0
    
    def test_load_from_csv_nonexistent_file(self, temp_csv_file):
        # Remove the file if it exists
        if os.path.exists(temp_csv_file):
            os.unlink(temp_csv_file)
        
        # Creating bank should not raise error
        bank = Bank(temp_csv_file)
        assert len(bank) == 0
    
    def test_get_bank_summary_with_accounts(self, bank):
        bank.create_account("Account A", 100.0)
        bank.create_account("Account B", 200.0)
        bank.create_account("Account C", 50.0)
        
        summary = bank.get_bank_summary()
        
        assert summary['total_accounts'] == 3
        assert summary['total_balance'] == 350.0
        assert summary['average_balance'] == pytest.approx(116.67, rel=1e-2)
        assert summary['min_balance'] == 50.0
        assert summary['max_balance'] == 200.0 
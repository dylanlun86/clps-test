import pytest
import os
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import patch

from banking_system.bank import Bank


class TestBankEdgeCases:
    
    @pytest.fixture
    def temp_csv_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name
        yield csv_path
        # Cleanup
        if os.path.exists(csv_path):
            os.unlink(csv_path)
    
    def test_transfer_rollback_on_deposit_failure(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        
        # Create accounts
        from_account_id = bank.create_account("Alice", 100.0)
        to_account_id = bank.create_account("Bob", 50.0)
        
        # Mock the deposit method to raise an exception
        from_account = bank.get_account(from_account_id)
        to_account = bank.get_account(to_account_id)
        
        original_deposit = to_account.deposit
        
        def mock_deposit_failure(*args, **kwargs):
            raise Exception("Simulated deposit failure")
        
        # Test the rollback scenario
        with patch.object(to_account, 'deposit', side_effect=mock_deposit_failure):
            with pytest.raises(Exception) as exc_info:
                bank.transfer(from_account_id, to_account_id, 30.0)
            
            assert "Simulated deposit failure" in str(exc_info.value)
            
            # Verify rollback occurred - from_account should still have original balance
            assert bank.get_balance(from_account_id) == 100.0
            assert bank.get_balance(to_account_id) == 50.0
    
    def test_save_csv_error_handling(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        account_id = bank.create_account("Test User", 100.0)
        
        # Mock pandas to_csv to raise an exception
        with patch('pandas.DataFrame.to_csv', side_effect=Exception("CSV write error")):
            with pytest.raises(Exception) as exc_info:
                bank.save_to_csv()
            
            assert "CSV write error" in str(exc_info.value)
    
    def test_load_csv_with_missing_columns(self, temp_csv_file):
        # Create CSV with missing columns
        df = pd.DataFrame({
            'account_id': ['test123'],
            'name': ['Test User']
            # Missing 'balance' and 'created_at' columns
        })
        df.to_csv(temp_csv_file, index=False)
        
        with pytest.raises(ValueError) as exc_info:
            Bank(temp_csv_file)
        
        assert "CSV missing required columns" in str(exc_info.value)
        assert "balance" in str(exc_info.value)
        assert "created_at" in str(exc_info.value)
    
    def test_load_csv_with_corrupted_account_data(self, temp_csv_file):
        # Create CSV with corrupted data - both rows will fail due to invalid types
        df = pd.DataFrame({
            'account_id': ['test123', 'test456'],
            'name': ['Valid User', 'Invalid User'],
            'balance': [100.0, 'invalid_balance'],  # Invalid balance
            'created_at': ['2024-01-01T10:00:00', 'invalid_date']  # Invalid date
        })
        df.to_csv(temp_csv_file, index=False)
        
        # Both accounts will fail to load due to pandas type comparison issues
        bank = Bank(temp_csv_file)
        
        # Should have loaded no accounts due to data corruption
        assert len(bank) == 0
    
    def test_load_csv_general_error_handling(self, temp_csv_file):
        # Create a file that will cause pandas.read_csv to fail
        with open(temp_csv_file, 'w') as f:
            f.write("invalid,csv,content\n")
            f.write("with,mismatched,columns,count\n")
        
        # Mock read_csv to raise a different kind of exception
        with patch('pandas.read_csv', side_effect=Exception("Pandas read error")):
            with pytest.raises(Exception) as exc_info:
                Bank(temp_csv_file)
            
            assert "Pandas read error" in str(exc_info.value)
    
    def test_save_csv_empty_bank(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        
        # Manually call save_to_csv on empty bank
        bank.save_to_csv()
        
        # Verify empty CSV with headers was created
        assert os.path.exists(temp_csv_file)
        df = pd.read_csv(temp_csv_file)
        assert df.empty
        assert list(df.columns) == ['account_id', 'name', 'balance', 'created_at']
    
    def test_load_csv_account_creation_failure(self, temp_csv_file):
        # Create valid CSV data
        df = pd.DataFrame({
            'account_id': ['test123'],
            'name': ['Test User'],
            'balance': [100.0],
            'created_at': ['2024-01-01T10:00:00']
        })
        df.to_csv(temp_csv_file, index=False)
        
        # Mock Account.from_dict to fail
        with patch('banking_system.bank.Account.from_dict', side_effect=Exception("Account creation failed")):
            bank = Bank(temp_csv_file)
            
            # Should handle the error gracefully and load 0 accounts
            assert len(bank) == 0
    
    def test_account_serialization_error(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        account_id = bank.create_account("Test User", 100.0)
        
        # Mock account.to_dict to fail
        account = bank.get_account(account_id)
        with patch.object(account, 'to_dict', side_effect=Exception("Serialization failed")):
            with pytest.raises(Exception):
                bank.save_to_csv()

    def test_load_csv_file_does_not_exist(self, temp_csv_file):
        # Create bank with existing file first, then delete it and call load_from_csv
        bank = Bank("dummy.csv")  # Use dummy to avoid auto-loading
        
        # Delete temp file to ensure it doesn't exist
        if os.path.exists(temp_csv_file):
            os.unlink(temp_csv_file)
        
        # Set the file path to the non-existent file and manually call load_from_csv
        bank._csv_file = Path(temp_csv_file)
        bank.load_from_csv()  # This should hit lines 214-215
        assert len(bank) == 0

    def test_load_csv_empty_data_error(self, temp_csv_file):
        # Create a CSV file with just whitespace (triggers EmptyDataError)
        with open(temp_csv_file, 'w') as f:
            f.write('   \n  \n  ')  # Only whitespace, triggers EmptyDataError
        
        # Create bank with existing file, then manually call load_from_csv to trigger the error
        bank = Bank("dummy.csv")  # Use dummy to avoid auto-loading
        bank._csv_file = Path(temp_csv_file)  # Set the file to our empty file
        bank.load_from_csv()  # This should hit lines 226-227
        assert len(bank) == 0

    def test_load_csv_empty_dataframe(self, temp_csv_file):
        # Create CSV with only headers but no data rows
        with open(temp_csv_file, 'w') as f:
            f.write('account_id,name,balance,created_at\n')  # Headers only
        
        bank = Bank(temp_csv_file)
        assert len(bank) == 0


class TestBankCLIIntegration:
    
    @pytest.fixture
    def temp_csv_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name
        yield csv_path
        if os.path.exists(csv_path):
            os.unlink(csv_path)
    
    def test_bank_with_existing_csv_data(self, temp_csv_file):
        # Create initial bank and save data
        bank1 = Bank(temp_csv_file)
        account1_id = bank1.create_account("Alice", 500.0)
        account2_id = bank1.create_account("Bob", 300.0)
        
        # Perform some operations
        bank1.deposit(account1_id, 100.0)
        bank1.transfer(account1_id, account2_id, 200.0)
        
        # Create new bank instance - should load existing data
        bank2 = Bank(temp_csv_file)
        
        # Verify data persistence
        assert len(bank2) == 2
        assert bank2.get_balance(account1_id) == 400.0  # 500 + 100 - 200
        assert bank2.get_balance(account2_id) == 500.0  # 300 + 200
        
        # Verify accounts are fully functional
        bank2.withdraw(account1_id, 50.0)
        assert bank2.get_balance(account1_id) == 350.0
    
    def test_concurrent_bank_instances(self, temp_csv_file):
        # Create first bank and add account
        bank1 = Bank(temp_csv_file)
        account_id = bank1.create_account("User1", 100.0)
        
        # Create second bank - should load the account
        bank2 = Bank(temp_csv_file)
        assert len(bank2) == 1
        assert account_id in bank2
        
        # Operations on bank1 save to CSV
        bank1.deposit(account_id, 50.0)
        
        # New bank3 should see the updated balance
        bank3 = Bank(temp_csv_file)
        assert bank3.get_balance(account_id) == 150.0
    
    def test_bank_file_path_edge_cases(self):
        # Test with relative path
        bank1 = Bank("./test_bank.csv")
        account_id = bank1.create_account("Test User", 100.0)
        assert os.path.exists("./test_bank.csv")
        
        # Test with absolute path
        abs_path = os.path.abspath("test_bank_abs.csv")
        bank2 = Bank(abs_path)
        account_id2 = bank2.create_account("Test User 2", 200.0)
        assert os.path.exists(abs_path)
        
        # Cleanup
        if os.path.exists("./test_bank.csv"):
            os.unlink("./test_bank.csv")
        if os.path.exists(abs_path):
            os.unlink(abs_path)


class TestBankPerformanceEdgeCases:
    
    @pytest.fixture
    def temp_csv_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name
        yield csv_path
        if os.path.exists(csv_path):
            os.unlink(csv_path)
    
    def test_large_number_of_accounts(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        account_ids = []
        
        # Create 100 accounts
        for i in range(100):
            account_id = bank.create_account(f"User{i}", float(i * 10))
            account_ids.append(account_id)
        
        assert len(bank) == 100
        
        # Test summary with many accounts
        summary = bank.get_bank_summary()
        assert summary['total_accounts'] == 100
        assert summary['total_balance'] == sum(i * 10 for i in range(100))
        assert summary['min_balance'] == 0.0
        assert summary['max_balance'] == 990.0
        
        # Test CSV persistence with large data
        bank2 = Bank(temp_csv_file)
        assert len(bank2) == 100
        
        # Verify a few random accounts
        assert bank2.get_balance(account_ids[0]) == 0.0
        assert bank2.get_balance(account_ids[50]) == 500.0
        assert bank2.get_balance(account_ids[99]) == 990.0
    
    def test_very_large_amounts(self, temp_csv_file):
        bank = Bank(temp_csv_file)
        
        # Test with billions
        large_amount = 1_000_000_000.00  # 1 billion
        account_id = bank.create_account("Billionaire", large_amount)
        
        assert bank.get_balance(account_id) == large_amount
        
        # Test operations with large amounts
        bank.deposit(account_id, 500_000_000.00)
        assert bank.get_balance(account_id) == 1_500_000_000.00
        
        bank.withdraw(account_id, 250_000_000.00)
        assert bank.get_balance(account_id) == 1_250_000_000.00
        
        # Test persistence of large amounts
        bank2 = Bank(temp_csv_file)
        assert bank2.get_balance(account_id) == 1_250_000_000.00 
import logging
from pathlib import Path
from typing import Dict, List
import pandas as pd

from .account import Account
from .exceptions import AccountNotFoundError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Bank:
    
    def __init__(self, csv_file: str = "bank_accounts.csv") -> None:

        self._accounts: Dict[str, Account] = {}
        self._csv_file = Path(csv_file)
        self._logger = logging.getLogger(f"{__name__}.Bank")
        
        # Load existing accounts if CSV file exists
        if self._csv_file.exists():
            self.load_from_csv()
    
    def create_account(self, name: str, initial_balance: float = 0.0) -> str:

        if not name.strip():
            raise ValueError("Account name cannot be empty")
            
        account = Account(name, initial_balance)
        account_id = account.account_id
        
        self._accounts[account_id] = account
        self._logger.info(f"Created account {account_id} for {name} with balance ${initial_balance:.2f}")
        
        # Auto-save after creating account
        self.save_to_csv()
        
        return account_id
    
    def get_account(self, account_id: str) -> Account:

        if account_id not in self._accounts:
            raise AccountNotFoundError(account_id)
        return self._accounts[account_id]
    
    def list_accounts(self) -> List[Account]:
        """Get a list of all accounts.
        
        Returns:
            List of all Account objects
        """
        return list(self._accounts.values())
    
    def deposit(self, account_id: str, amount: float) -> None:

        account = self.get_account(account_id)
        account.deposit(amount)
        
        self._logger.info(f"Deposited ${amount:.2f} to account {account_id}")
        self.save_to_csv()
    
    def withdraw(self, account_id: str, amount: float) -> None:

        account = self.get_account(account_id)
        account.withdraw(amount)
        
        self._logger.info(f"Withdrew ${amount:.2f} from account {account_id}")
        self.save_to_csv()
    
    def transfer(self, from_account_id: str, to_account_id: str, amount: float) -> None:

        if from_account_id == to_account_id:
            raise ValueError("Cannot transfer to the same account")
            
        # Validate both accounts exist before attempting transfer
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)
        
        # Perform the transfer (atomic operation)
        from_account.withdraw(amount)
        try:
            to_account.deposit(amount)
        except Exception as e:
            # Rollback if deposit fails
            from_account.deposit(amount)
            raise e
        
        self._logger.info(
            f"Transferred ${amount:.2f} from {from_account_id} to {to_account_id}"
        )
        self.save_to_csv()
    
    def get_balance(self, account_id: str) -> float:

        account = self.get_account(account_id)
        return account.balance
    
    def save_to_csv(self) -> None:

        try:
            # Convert accounts to list of dictionaries
            accounts_data = [account.to_dict() for account in self._accounts.values()]
            
            if accounts_data:
                # Use pandas for robust CSV handling
                df = pd.DataFrame(accounts_data)
                df.to_csv(self._csv_file, index=False, float_format='%.2f')
                self._logger.info(f"Saved {len(accounts_data)} accounts to {self._csv_file}")
            else:
                # Create empty CSV with headers
                pd.DataFrame(columns=['account_id', 'name', 'balance', 'created_at']).to_csv(
                    self._csv_file, index=False
                )
                self._logger.info(f"Created empty CSV file: {self._csv_file}")
                
        except Exception as e:
            self._logger.error(f"Failed to save accounts to CSV: {e}")
            raise
    
    def load_from_csv(self) -> None:

        try:
            if not self._csv_file.exists():
                self._logger.info(f"CSV file {self._csv_file} does not exist")
                return
            
            # Check if file is empty or just contains whitespace
            if self._csv_file.stat().st_size == 0:
                self._logger.info("CSV file is empty")
                return
                
            # Use pandas for robust CSV reading
            try:
                df = pd.read_csv(self._csv_file)
            except pd.errors.EmptyDataError:
                self._logger.info("CSV file contains no data")
                return
            
            if df.empty:
                self._logger.info("CSV file is empty")
                return
                
            # Validate required columns
            required_columns = {'account_id', 'name', 'balance', 'created_at'}
            if not required_columns.issubset(df.columns):
                missing_cols = required_columns - set(df.columns)
                raise ValueError(f"CSV missing required columns: {missing_cols}")
            
            # Load accounts
            loaded_count = 0
            for _, row in df.iterrows():
                try:
                    account_data = row.to_dict()
                    account = Account.from_dict(account_data)
                    self._accounts[account.account_id] = account
                    loaded_count += 1
                except Exception as e:
                    self._logger.warning(f"Failed to load account from row {row.name}: {e}")
                    continue
            
            self._logger.info(f"Loaded {loaded_count} accounts from {self._csv_file}")
            
        except Exception as e:
            self._logger.error(f"Failed to load accounts from CSV: {e}")
            raise
    
    def get_bank_summary(self) -> Dict[str, any]:

        accounts = list(self._accounts.values())
        total_accounts = len(accounts)
        
        if total_accounts == 0:
            return {
                'total_accounts': 0,
                'total_balance': 0.0,
                'average_balance': 0.0,
                'min_balance': 0.0,
                'max_balance': 0.0
            }
        
        balances = [account.balance for account in accounts]
        total_balance = sum(balances)
        
        return {
            'total_accounts': total_accounts,
            'total_balance': total_balance,
            'average_balance': total_balance / total_accounts,
            'min_balance': min(balances),
            'max_balance': max(balances)
        }
    
    def __len__(self) -> int:

        return len(self._accounts)
    
    def __contains__(self, account_id: str) -> bool:

        return account_id in self._accounts 
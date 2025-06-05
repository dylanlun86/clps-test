import sys

from .bank import Bank
from .exceptions import (
    BankingException,
    AccountNotFoundError
)


class BankingCLI:
    
    def __init__(self, csv_file: str = "bank_accounts.csv") -> None:

        self.bank = Bank(csv_file)
        self.running = True
    
    def display_menu(self) -> None:

        print("\n" + "="*50)
        print("         SIMPLE BANKING SYSTEM")
        print("="*50)
        print("1. Create Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Money")
        print("5. Check Balance")
        print("6. List All Accounts")
        print("7. Bank Summary")
        print("8. Exit")
        print("="*50)
    
    def get_user_input(self, prompt: str, input_type: type = str) -> any:

        while True:
            try:
                user_input = input(f"{prompt}: ").strip()
                if input_type == str:
                    if not user_input:
                        print("Input cannot be empty. Please try again.")
                        continue
                    return user_input
                elif input_type == float:
                    value = float(user_input)
                    if value < 0:
                        print("Amount cannot be negative. Please try again.")
                        continue
                    return value
                elif input_type == int:
                    return int(user_input)
                else:
                    return input_type(user_input)
            except ValueError:
                print(f"Invalid input. Please enter a valid {input_type.__name__}.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return None
    
    def create_account(self) -> None:

        print("\n--- Create New Account ---")
        
        name = self.get_user_input("Enter account holder name")
        if name is None:
            return
            
        initial_balance = self.get_user_input(
            "Enter initial balance (default: 0.00)", 
            float
        )
        if initial_balance is None:
            return
        
        try:
            account_id = self.bank.create_account(name, initial_balance)
            print(f"\n✅ Account created successfully!")
            print(f"Account ID: {account_id}")
            print(f"Account Holder: {name}")
            print(f"Initial Balance: ${initial_balance:.2f}")
        except BankingException as e:
            print(f"\n❌ Error creating account: {e}")
    
    def deposit_money(self) -> None:

        print("\n--- Deposit Money ---")
        
        account_id = self.get_user_input("Enter account ID")
        if account_id is None:
            return
            
        amount = self.get_user_input("Enter deposit amount", float)
        if amount is None:
            return
        
        try:
            self.bank.deposit(account_id, amount)
            new_balance = self.bank.get_balance(account_id)
            print(f"\n✅ Deposit successful!")
            print(f"Deposited: ${amount:.2f}")
            print(f"New Balance: ${new_balance:.2f}")
        except BankingException as e:
            print(f"\n❌ Error during deposit: {e}")
    
    def withdraw_money(self) -> None:

        print("\n--- Withdraw Money ---")
        
        account_id = self.get_user_input("Enter account ID")
        if account_id is None:
            return
            
        try:
            current_balance = self.bank.get_balance(account_id)
            print(f"Current Balance: ${current_balance:.2f}")
        except AccountNotFoundError as e:
            print(f"\n❌ {e}")
            return
            
        amount = self.get_user_input("Enter withdrawal amount", float)
        if amount is None:
            return
        
        try:
            self.bank.withdraw(account_id, amount)
            new_balance = self.bank.get_balance(account_id)
            print(f"\n✅ Withdrawal successful!")
            print(f"Withdrawn: ${amount:.2f}")
            print(f"New Balance: ${new_balance:.2f}")
        except BankingException as e:
            print(f"\n❌ Error during withdrawal: {e}")
    
    def transfer_money(self) -> None:

        print("\n--- Transfer Money ---")
        
        from_account = self.get_user_input("Enter source account ID")
        if from_account is None:
            return
            
        to_account = self.get_user_input("Enter destination account ID")
        if to_account is None:
            return
        
        try:
            from_balance = self.bank.get_balance(from_account)
            to_balance = self.bank.get_balance(to_account)
            print(f"Source Account Balance: ${from_balance:.2f}")
            print(f"Destination Account Balance: ${to_balance:.2f}")
        except AccountNotFoundError as e:
            print(f"\n❌ {e}")
            return
            
        amount = self.get_user_input("Enter transfer amount", float)
        if amount is None:
            return
        
        try:
            self.bank.transfer(from_account, to_account, amount)
            new_from_balance = self.bank.get_balance(from_account)
            new_to_balance = self.bank.get_balance(to_account)
            
            print(f"\n✅ Transfer successful!")
            print(f"Transferred: ${amount:.2f}")
            print(f"Source Account New Balance: ${new_from_balance:.2f}")
            print(f"Destination Account New Balance: ${new_to_balance:.2f}")
        except BankingException as e:
            print(f"\n❌ Error during transfer: {e}")
    
    def check_balance(self) -> None:

        print("\n--- Check Balance ---")
        
        account_id = self.get_user_input("Enter account ID")
        if account_id is None:
            return
        
        try:
            account = self.bank.get_account(account_id)
            print(f"\n💰 Account Information:")
            print(f"Account ID: {account.account_id}")
            print(f"Account Holder: {account.name}")
            print(f"Current Balance: ${account.balance:.2f}")
            print(f"Account Created: {account.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        except AccountNotFoundError as e:
            print(f"\n❌ {e}")
    
    def list_accounts(self) -> None:

        print("\n--- All Accounts ---")
        
        accounts = self.bank.list_accounts()
        if not accounts:
            print("No accounts found.")
            return
        
        print(f"\nTotal Accounts: {len(accounts)}")
        print("-" * 70)
        print(f"{'ID':<10} {'Name':<20} {'Balance':<15} {'Created':<20}")
        print("-" * 70)
        
        for account in sorted(accounts, key=lambda x: x.created_at):
            print(f"{account.account_id:<10} {account.name:<20} "
                  f"${account.balance:<14.2f} "
                  f"{account.created_at.strftime('%Y-%m-%d %H:%M'):<20}")
    
    def show_bank_summary(self) -> None:

        print("\n--- Bank Summary ---")
        
        summary = self.bank.get_bank_summary()
        
        print(f"\n Banking System Statistics:")
        print(f"Total Accounts: {summary['total_accounts']}")
        print(f"Total Bank Balance: ${summary['total_balance']:.2f}")
        
        if summary['total_accounts'] > 0:
            print(f"Average Account Balance: ${summary['average_balance']:.2f}")
            print(f"Minimum Account Balance: ${summary['min_balance']:.2f}")
            print(f"Maximum Account Balance: ${summary['max_balance']:.2f}")
    
    def run(self) -> None:

        print("Welcome to the Simple Banking System!")
        print("Data will be automatically saved to CSV file.")
        
        while self.running:
            try:
                self.display_menu()
                choice = self.get_user_input("Enter your choice (1-8)", str)
                
                if choice is None:
                    continue
                
                if choice == "1":
                    self.create_account()
                elif choice == "2":
                    self.deposit_money()
                elif choice == "3":
                    self.withdraw_money()
                elif choice == "4":
                    self.transfer_money()
                elif choice == "5":
                    self.check_balance()
                elif choice == "6":
                    self.list_accounts()
                elif choice == "7":
                    self.show_bank_summary()
                elif choice == "8":
                    print("\nThank you for using the Simple Banking System!")
                    print("All data has been saved automatically.")
                    self.running = False
                else:
                    print("\n❌ Invalid choice. Please select 1-8.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting Banking System...")
                self.running = False
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("Please try again or contact support.")


def main() -> None:
    """Entry point for the CLI application."""
    try:
        cli = BankingCLI()
        cli.run()
    except Exception as e:
        print(f"Failed to start banking system: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
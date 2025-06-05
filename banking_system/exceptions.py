class BankingException(Exception):
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InsufficientFundsError(BankingException):
    
    def __init__(self, account_id: str, requested_amount: float, current_balance: float) -> None:
        message = (
            f"Insufficient funds in account {account_id}. "
            f"Requested: ${requested_amount:.2f}, Available: ${current_balance:.2f}"
        )
        super().__init__(message)
        self.account_id = account_id
        self.requested_amount = requested_amount
        self.current_balance = current_balance


class AccountNotFoundError(BankingException):
    
    def __init__(self, account_id: str) -> None:
        message = f"Account with ID '{account_id}' not found"
        super().__init__(message)
        self.account_id = account_id


class InvalidAmountError(BankingException):
    
    def __init__(self, amount: float) -> None:
        message = f"Invalid amount: ${amount:.2f}. Amount must be positive."
        super().__init__(message)
        self.amount = amount


class DuplicateAccountError(BankingException):
    
    def __init__(self, account_id: str) -> None:
        message = f"Account with ID '{account_id}' already exists"
        super().__init__(message)
        self.account_id = account_id 
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any
import uuid

from .exceptions import InvalidAmountError, InsufficientFundsError


class Account:
    
    def __init__(self, name: str, initial_balance: float = 0.0) -> None:

        if initial_balance < 0:
            raise InvalidAmountError(initial_balance)
            
        self._account_id = str(uuid.uuid4())[:8]  # Short UUID for readability
        self._name = name.strip()
        self._balance = Decimal(str(initial_balance)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        self._created_at = datetime.now()
        
    @property
    def account_id(self) -> str:

        return self._account_id
    
    @property
    def name(self) -> str:

        return self._name
    
    @property
    def balance(self) -> float:

        return float(self._balance)
    
    @property
    def created_at(self) -> datetime:

        return self._created_at
    
    def deposit(self, amount: float) -> None:

        if amount <= 0:
            raise InvalidAmountError(amount)
            
        decimal_amount = Decimal(str(amount)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        self._balance += decimal_amount
    
    def withdraw(self, amount: float) -> None:

        if amount <= 0:
            raise InvalidAmountError(amount)
            
        decimal_amount = Decimal(str(amount)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        if decimal_amount > self._balance:
            raise InsufficientFundsError(
                self._account_id, 
                float(decimal_amount), 
                float(self._balance)
            )
            
        self._balance -= decimal_amount
    
    def to_dict(self) -> Dict[str, Any]:

        return {
            'account_id': self._account_id,
            'name': self._name,
            'balance': float(self._balance),
            'created_at': self._created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':

        account = cls(data['name'], data['balance'])
        account._account_id = data['account_id']
        account._created_at = datetime.fromisoformat(data['created_at'])
        return account
    
    def __str__(self) -> str:

        return f"Account({self._account_id}, {self._name}, ${self.balance:.2f})"
    
    def __repr__(self) -> str:

        return (
            f"Account(account_id='{self._account_id}', name='{self._name}', "
            f"balance={self.balance:.2f}, created_at='{self._created_at.isoformat()}')"
        ) 
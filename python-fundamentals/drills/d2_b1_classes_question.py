def raises(exc_type, fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except exc_type:
        return True
    return False


class BankAccount:
    def __init__(self, owner: str, balance: float = 0) -> None:
        self.owner = owner
        self._balance = balance  # internal

    @property
    def balance(self) -> float:
        return self._balance

    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self._balance:,.1f})"

    def withdraw(self, amount: float) -> None:
        self._validate_amount(amount)

        if amount > self._balance:
            raise ValueError("Insufficient balance")
        self._balance -= amount

    def deposit(self, amount: float) -> None:
        self._validate_amount(amount)
        self._balance += amount

    def _validate_amount(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

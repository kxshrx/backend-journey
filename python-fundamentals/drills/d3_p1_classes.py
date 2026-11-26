# # class BankAccount:
# #     def __init__(self, owner:str, balance:float=0)->None:
# #         self.owner=owner
# #         self.balance=balance

# #     def deposit(self,amount:float):
# #         self.balance+=amount
# #         return f"Amount {amount} deposited successfully. Available balance is {self.balance}"

# from dataclasses import dataclass


# @dataclass
# class BankAccount:
#     owner: str
#     _balance: float

#     @property
#     def balance(self) -> float:
#         return self._balance

#     @balance.setter
#     def balance(self, bal:float)->None:
#         self._balance=bal

#     def deposit(self, amount: float) -> float:
#         self.balance += amount
#         return f"Amount {amount} deposited successfully. Available balance is {self.balance}"


# acct = BankAccount("kishore", 1000)
# print(acct)

# acct.deposit(500)
# print(acct)

# # print(acct.balance())
# print(acct.balance)
# acct.balance = 200
# print(acct.balance)


# # P1
# class Counter:
#     count = 0
#     def __init__(self):
#         Counter.count += 1
# a = Counter(); b = Counter()
# print(Counter.count, a.count, b.count)

# # P2
# class A:
#     def __init__(self):
#         self.items = []
# x, y = A(), A()
# x.items.append(1)
# print(y.items)

# # P3
# class P:
#     def __init__(self, v):
#         self.v = v
# p = P(1)
# q = p
# q.v = 2
# print(p.v)

# # P4
# from dataclasses import dataclass
# @dataclass
# class T:
#     a: int
# print(T(1) == T(1), T(1) is T(1))


def raises(exc_type, fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except exc_type:
        return True
    return False


class BankAccount:
    def __init__(self, owner: str, balance: float = 0):
        self.owner = owner
        self._balance = balance

    def __repr__(self):
        return f"BankAccount(owner={self.owner!r}, balance={self._balance})"

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError
        self._balance += amount
        # return f"Available balance {self.balance}"

    def withdraw(self, amount: float):
        if amount <= 0 or self._balance - amount < 0:
            raise ValueError
        self._balance -= amount
        # return f"Available balance {self.balance}"


# =======

from dataclasses import dataclass, field


@dataclass
class Playlist:
    name: str
    songs: list[str] = field(default_factory=list)


# ========


@dataclass
class User:
    name: str
    age: int

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(name=data["name"], age=int(data["age"]))


from dataclasses import asdict     # (imports at the top of the file)

acc = BankAccount("asha", 100)
acc.deposit(50.5)
acc.withdraw(50)
assert acc.balance == 100.5
assert repr(acc) == "BankAccount(owner='asha', balance=100.5)"
assert raises(ValueError, acc.deposit, 0)
assert raises(ValueError, acc.deposit, -5)
assert raises(ValueError, acc.withdraw, 1000)
assert raises(AttributeError, setattr, acc, "balance", 5)

a, b = Playlist("a"), Playlist("b")
a.songs.append("s1")
assert b.songs == []
assert asdict(a) == {"name": "a", "songs": ["s1"]}

u = User.from_dict({"name": "Asha", "age": "30"})
assert u == User("Asha", 30)
assert raises(KeyError, User.from_dict, {"name": "x"})
print("D3 P1 OK")

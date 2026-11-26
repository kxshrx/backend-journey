# Day 3 · Tuesday 24 Nov: Python catch-up: classes, errors, modules

> Module 1, Day 3 of 30 · about 4 hours including breaks · written for a **Mac**
> **Everything you need for today is in this file.** Don't look anything else up.
> Save it as `notes/days/day-03.md` in your `backend-journey` repo.

---

## Read this first

You stopped last time at **inheritance and polymorphism**. That's the spot where almost everyone stops, because it's explained badly almost everywhere. Today it gets its **own slow part (Part 2)**, with pictures, step-by-step traces and tiny examples.

**The only goal for Part 2 is three sentences:**
1. A **child class gets everything its parent has**.
2. The child can **replace** (override) parts of it.
3. Code written for the **parent works for every child**: the *same call* does *different things*. (That's "polymorphism".)

If you can say those three sentences in your own words by tonight, **the day is a success**, even if you do nothing else well.

Feeling slow with code is normal after time away. Nothing today needs speed. Each part has a stopping point.

---

## How today works

| Part | Time | What |
|---|---|---|
| Check-in | 5 min | **Recall** 3 things from yesterday without looking; write "today I'm done when…" in `journal.md` |
| **Part 1** | 50 min | Classes from scratch |
| Break | 5 min | Walk, water |
| **Part 2** | 45 min | **Inheritance and polymorphism** (the slow one) |
| Break | 10 min | Eat something |
| **Part 3** | 50 min | Errors and exceptions |
| **Part 4** | 35 min | Modules, packages, imports |
| Wrap-up | 10 min | Questions, cheat sheet, commit |

**Floor rule (zero-energy day):** Part 2 alone counts as a day.
**Placement rule:** if you already have a classes drill file from before and its `OK` line prints, skim Part 1 (do the "Check yourself" box only) and start Part 2.

**How the exercises work**
- Put each part's code in `python-fundamentals/drills/` (file names are given). Run from the `python-fundamentals` folder: `uv run python drills/<file>.py`.
- Each exercise block ends with `assert` lines. If your code is right nothing happens and the last line prints `OK`. If something is wrong you get an `AssertionError` with a line number: fix **your code**, never the asserts.
- **Predict the output:** write your guess *first*, then run it. Wrong guesses are the best learning: write one sentence in `notes/00-python-cheatsheet.md` for each one you miss. Answers are at the bottom.
- **Stuck?** 5 minutes → write `TODO` in your journal and move on · 20 minutes → ask an AI for a *hint* using the prompt in `01-fastapi-start-here.md` · **Solutions are at the bottom**: read one only after 20 minutes of trying, then close the file and retype it from memory.

Paste this helper at the top of every drill file today (you'll use it in the self-checks):
```python
def raises(exc_type, fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except exc_type:
        return True
    return False
```

---

# Part 1 · Classes from scratch (50 min)

> **Check yourself (5 min):** write `BankAccount` (exercise 1 below) without reading this part. If it works first time, skim to the end of Part 1 and go to Part 2.

### 1.1 Why classes exist
A class **bundles data with the functions that work on that data**.

Without a class you might write:
```python
account = {"owner": "asha", "balance": 100}

def deposit(account, amount):
    account["balance"] += amount
```
It works, but the data and the functions are separate, nothing stops you putting `"blanace"` in a dict by mistake, and nothing says which functions belong with which data. A class puts them together.

**Why you care:** in your backend, *everything* is a class: a Pydantic model (`class Project(BaseModel)`), a database table (`class Project(Base)`), an error (`class NotFound(Exception)`), a settings object. You must be able to **read and write them**.

### 1.2 Blueprint and objects
- A **class** is a **blueprint** (like a cookie cutter, or the plan for a house).
- An **object** (also called an **instance**) is one thing built from that blueprint (one cookie, one house).

`BankAccount` is the class. `acct = BankAccount("asha", 100)` builds **one object**. You can build as many as you like; each has its own data.

### 1.3 The anatomy, with a trace
```python
class BankAccount:
    def __init__(self, owner: str, balance: float = 0) -> None:
        self.owner = owner
        self._balance = balance

    def deposit(self, amount: float) -> None:
        self._balance += amount


acct = BankAccount("asha", 100)
acct.deposit(50)
```
**What happens at `BankAccount("asha", 100)`:**
1. Python creates a **new, empty object**.
2. It calls `__init__` on it: `__init__(that_new_object, "asha", 100)`. Inside, **`self` is that new object**.
3. `self.owner = owner` **stores** `"asha"` *on the object*. Same for `_balance`.
4. The finished object is assigned to the name `acct`.

**And `acct.deposit(50)`** is just a prettier way of writing `BankAccount.deposit(acct, 50)`. That's what `self` is: **the object the method was called on.** It's always the first parameter of a method, and you never pass it yourself.

Vocabulary:
- **Attributes** = the data stored on an object (`self.owner`).
- **Methods** = functions defined inside the class (`deposit`).
- A name starting with **`_`** (like `_balance`) means "internal, please don't touch from outside". It's a convention, not a lock.

### 1.4 `__repr__`: how an object shows itself
Print a plain object and you get something useless like `<__main__.BankAccount object at 0x104a…>`. Define `__repr__` to make it readable (very helpful when debugging):
```python
    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self._balance})"

print(acct)       # BankAccount(owner='asha', balance=150)
```

### 1.5 Instance attributes vs class attributes
```python
class Counter:
    count = 0                      # class attribute: ONE copy shared by every object

    def __init__(self):
        Counter.count += 1         # modifies the shared one
        self.id = Counter.count    # instance attribute: each object has its own
```
**Instance attributes** (set with `self.…` in methods) are per-object. **Class attributes** (written directly in the class body) are shared by all. Danger: a **mutable** class attribute (`items = []`) is shared by every object, the same trap as the mutable default argument.

### 1.6 `@property`: an attribute that is really a method
```python
    @property
    def balance(self) -> float:
        return self._balance

acct.balance          # 150    ← no parentheses, reads like an attribute
acct.balance = 5      # AttributeError: it's read-only (there's no setter)
```
Use it to expose a value but **stop outsiders from overwriting it directly**: they must go through `deposit` / `withdraw`, which can check the rules.

### 1.7 `@classmethod`: an alternative way to build an object
```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    @classmethod
    def from_dict(cls, data: dict) -> "User":     # `cls` is the class itself (User)
        return cls(name=data["name"], age=int(data["age"]))

u = User.from_dict({"name": "Asha", "age": "30"})
```
A regular method receives the **object** (`self`). A class method receives the **class** (`cls`). Use it for "build me one from this other kind of input". (There is also `@staticmethod`, a plain function that lives inside the class; you'll rarely need it.)

### 1.8 `@dataclass`: less typing for classes that mostly hold data
```python
from dataclasses import asdict, dataclass, field

@dataclass
class Task:
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)   # safe default for a list

t = Task("write code")
print(t)                      # Task(title='write code', done=False, tags=[])
print(t == Task("write code"))  # True: compares field by field
print(asdict(t))              # {'title': 'write code', 'done': False, 'tags': []}
```
`@dataclass` **writes `__init__`, `__repr__` and `__eq__` for you** from the list of fields. **`field(default_factory=list)`** is the dataclass way of saying "a *new* empty list for each object" (never write `tags: list = []`).
Use a dataclass for **containers of data**; use a normal class when there's more behaviour and rules.

### 1.9 Common mistakes
- Forgetting `self` as the first parameter of a method, or forgetting `self.` when setting an attribute (`owner = owner` does nothing useful).
- Calling a method **without parentheses** (`acct.deposit` is the method itself, not a call).
- A mutable class attribute or default (`items = []`) shared by every object.

### Type it → `drills/d3_p1_classes.py`
Type every example from 1.3 to 1.8 into the file, run it, change a value, and break it on purpose (for example set `acct.balance = 5`).

### Predict the output (guess first; answers at the bottom)
```python
# P1
class Counter:
    count = 0
    def __init__(self):
        Counter.count += 1
a = Counter(); b = Counter()
print(Counter.count, a.count, b.count)

# P2
class A:
    def __init__(self):
        self.items = []
x, y = A(), A()
x.items.append(1)
print(y.items)

# P3
class P:
    def __init__(self, v):
        self.v = v
p = P(1)
q = p
q.v = 2
print(p.v)

# P4
from dataclasses import dataclass
@dataclass
class T:
    a: int
print(T(1) == T(1), T(1) is T(1))
```

### Exercises: Part 1
1. **`BankAccount(owner: str, balance: float = 0)`**: `deposit(amount)` and `withdraw(amount)` raise `ValueError` when `amount <= 0`, or when withdrawing more than the balance. `balance` is a **read-only property**. `__repr__` is `BankAccount(owner='asha', balance=100.5)`.
2. **`@dataclass class Playlist`** with `name: str` and `songs: list[str]` (safe default).
3. **`@dataclass class User`** (`name: str`, `age: int`) with a **`@classmethod from_dict(cls, data: dict) -> "User"`** that converts `age` with `int()`.

**Self-check**
```python
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
```

**Part 1 done when**
- [ ] `D3 P1 OK` prints
- [ ] You can explain what `self` is and what `__init__` does, in your own words
- [ ] Predict answers checked, with a cheat-sheet line for each miss

---

# Part 2 · Inheritance and polymorphism (45 min)

*Go slowly. Re-read each section once. The code is short on purpose.*

### 2.1 The problem inheritance solves
Imagine you write a `Dog` class and a `Cat` class. Both need a `name`, and both need an `intro()` method. You'd copy and paste. Then a third animal, and a fourth. If you ever change `intro()`, you must change it in every copy.

**Inheritance** lets you write the shared part **once**, in a **parent class** (also called a *base class* or *superclass*), and let other classes **inherit** it.

### 2.2 The basic idea
```python
class Animal:                          # the parent
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "..."

    def intro(self) -> str:
        return f"{self.name} says {self.speak()}"


class Dog(Animal):                     # Dog inherits from Animal (the parent goes in brackets)
    def speak(self) -> str:            # ...and replaces speak()
        return "Woof"


class Cat(Animal):
    def speak(self) -> str:
        return "Meow"
```
Picture it as a family tree:
```
        Animal          ← has: name, speak(), intro()
        /    \
      Dog    Cat        ← each is an Animal; each replaces speak()
```
Now:
```python
rex = Dog("Rex")
print(rex.name)      # Rex
print(rex.intro())   # Rex says Woof
```
**Notice what you did NOT write:** `Dog` has no `__init__` and no `intro`. It **inherits** both from `Animal`.

### 2.3 What Python does when you call `rex.intro()` (the lookup order)
Python needs to find `intro`. It searches in order:
1. the **object** `rex` itself (nothing there)
2. the object's **class**, `Dog` (no `intro` there)
3. the **parent**, `Animal` (found it!), so it runs it

Inside `intro`, the line `self.speak()` runs. **`self` is still `rex`, which is a `Dog`.** So Python searches for `speak` again, *starting at `Dog`*, and finds Dog's version first: `"Woof"`.

That's the key insight, and the reason the result is `Rex says Woof` and not `Rex says ...`:
> **Method lookup always starts at the object's real class and walks up the family tree.**

See the order Python walks: `print(Dog.__mro__)` gives `(Dog, Animal, object)`. (`object` is the parent of every class in Python.)

### 2.4 Overriding
When a child defines a method with **the same name** as its parent's, the child's version **replaces** it for the child's objects. That's *overriding*. `Dog.speak` overrides `Animal.speak`. An `Animal("X").speak()` still gives `"..."`.

### 2.5 `super()`: when the child needs the parent's version too
Often the child wants to **add to** the parent's behaviour, not throw it away.
```python
class Employee:
    def __init__(self, name: str, salary: int) -> None:
        self.name = name
        self.salary = salary

    def describe(self) -> str:
        return f"{self.name} earns {self.salary}"


class Manager(Employee):
    def __init__(self, name: str, salary: int, reports: list[str] | None = None) -> None:
        super().__init__(name, salary)            # run Employee's __init__ first
        self.reports = reports if reports is not None else []

    def describe(self) -> str:
        return f"{super().describe()} and manages {len(self.reports)} people"
```
`super()` means "**my parent's version**". Here:
- `super().__init__(name, salary)` sets up `name` and `salary` using the parent's code, so `Manager` only adds what's new (`reports`).
- `super().describe()` gets the parent's sentence, and the child adds to it.

**The #1 inheritance bug:** if a child defines its own `__init__`, Python **does not** call the parent's automatically. If you forget `super().__init__(...)`, the parent's attributes (`name`, `salary`) never get set. *Rule: when you write an `__init__` in a child, call `super().__init__(...)` first.*

### 2.6 `isinstance` and `issubclass`: the "is-a" relationship
```python
isinstance(rex, Dog)       # True
isinstance(rex, Animal)    # True   ← a Dog IS an Animal
isinstance(Animal("x"), Dog)   # False  ← an Animal is not necessarily a Dog
issubclass(Dog, Animal)    # True
```

### 2.7 Polymorphism: same call, different behaviour
*Poly* = many, *morph* = forms. **Polymorphism** means you can call the same method on different kinds of objects, and **each does its own thing**.
```python
def chorus(animals: list[Animal]) -> list[str]:
    return [f"{a.name}: {a.speak()}" for a in animals]

chorus([Dog("Rex"), Cat("Tom"), Animal("Generic")])
# ['Rex: Woof', 'Tom: Meow', 'Generic: ...']
```
Look at `chorus`: **there's no `if dog … elif cat …`.** It just calls `a.speak()` and trusts each object to know how. The payoff: if you add `class Cow(Animal)` tomorrow, `chorus` works with cows **without changing a single line**.

A realistic backend version:
```python
class Notifier:
    def send(self, message: str) -> None:
        raise NotImplementedError          # "children must provide this"

class EmailNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"emailing: {message}")

class SmsNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"texting: {message}")

def alert_all(notifiers: list[Notifier], message: str) -> None:
    for n in notifiers:
        n.send(message)                     # works for any kind of Notifier
```
(`raise NotImplementedError` in the parent is a common way to say "this is a template: every child must fill this in".)

### 2.8 Where you'll see this in your backend
- `class Project(BaseModel): name: str` means **Project inherits from BaseModel**. It *is a* BaseModel, so it gets validation, `.model_dump()` and more for free, and you only add your fields.
- `class NotFound(AppError)` and `class AppError(Exception)`: your own errors inherit from Python's `Exception`. That's why `except Exception:` catches *all* of them (polymorphism!).
- `class Project(Base)` for database tables (SQLAlchemy).

**You won't design big inheritance trees. You'll mostly *use* base classes that frameworks give you.** That's why "read it as: *X is a Y with extras*" is enough.

### 2.9 Inheritance vs composition (when NOT to inherit)
Ask the **"is-a" test**: *a Dog IS an Animal* ✓ → inheritance fits. *A Car IS an Engine* ✗ (a car **has** an engine) → use **composition**: store the other object as an attribute:
```python
class Engine: ...
class Car:
    def __init__(self):
        self.engine = Engine()      # a Car HAS an Engine
```
**Default to composition.** Use inheritance for true "is-a" specialisation and for framework base classes (`BaseModel`, `Exception`). Never inherit just to copy a few lines of code, and avoid long chains (A → B → C → D), which are hard to follow.

### 2.10 Common mistakes
- Forgetting `super().__init__(...)` in a child's `__init__`.
- Thinking a child's `__init__` automatically runs the parent's. It doesn't.
- Using inheritance when "has-a" is the right model.
- Checking types with `if type(x) == Dog` instead of letting polymorphism do the work.

### Type it → `drills/d3_p2_inheritance.py`
Type the `Animal`/`Dog`/`Cat`, `Employee`/`Manager`, and `Notifier` examples. Run each, and then:
- Add `print(Dog.__mro__)` and read it.
- Remove `super().__init__(name, salary)` from `Manager` and see the error when you read `.name`. (That's the #1 bug, on purpose.)
- Add a `class Cow(Animal)` and pass a cow into `chorus` without touching `chorus`.

### Predict the output (guess first; answers at the bottom)
```python
# P5
class Animal:
    def speak(self): return "..."
    def intro(self): return "I say " + self.speak()
class Dog(Animal):
    def speak(self): return "Woof"
print(Animal().intro(), Dog().intro())

# P6
class A:
    def __init__(self):
        print("A init")
class B(A):
    def __init__(self):
        print("B init")
B()

# P7
class C(A):
    def __init__(self):
        super().__init__()
        print("C init")
C()

# P8
print(isinstance(Dog(), Animal), isinstance(Animal(), Dog), issubclass(Dog, Animal))
```

### Exercises: Part 2
4. **`Animal(name)`** with `speak() -> str` returning `"..."`; **`Dog`** → `"Woof"`; **`Cat`** → `"Meow"`; and a function **`chorus(animals: list[Animal]) -> list[str]`** returning `"<name>: <sound>"` for each.
5. **`Shape`** with `area()` that raises `NotImplementedError`; **`Rectangle(width, height)`** and **`Circle(radius)`** (use `math.pi`) override `area()`; and **`total_area(shapes: list[Shape]) -> float`** that adds up the areas.
6. **`Employee(name, salary)`** with `describe()` → `"Ravi earns 50"`; **`Manager(Employee)`** adds a `reports` list (default: a **new** empty list per manager; careful with the default!) and its `describe()` → `"Asha earns 90 and manages 2 people"` using `super()`.

**Self-check** (put `import math` at the top of the file)
```python
pets = [Dog("Rex"), Cat("Tom"), Animal("Generic")]
assert chorus(pets) == ["Rex: Woof", "Tom: Meow", "Generic: ..."]
assert isinstance(pets[0], Animal) and not isinstance(pets[2], Dog)
assert issubclass(Cat, Animal)

assert Rectangle(3, 4).area() == 12
assert math.isclose(Circle(1).area(), math.pi)
assert raises(NotImplementedError, Shape().area)
assert math.isclose(total_area([Rectangle(2, 5), Circle(2)]), 10 + 4 * math.pi)

assert Employee("Ravi", 50).describe() == "Ravi earns 50"
assert Manager("Asha", 90, ["a", "b"]).describe() == "Asha earns 90 and manages 2 people"
assert isinstance(Manager("x", 1), Employee)
m1, m2 = Manager("x", 1), Manager("y", 2)
m1.reports.append("z")
assert m2.reports == []
print("D3 P2 OK")
```

### Say it back (the real test of Part 2)
Close this file. In `notes/00-python-cheatsheet.md`, write in your own words, one or two lines each:
1. What does a child class get from its parent?
2. What is overriding?
3. What does `super()` do, and what goes wrong if you forget `super().__init__(...)`?
4. What is polymorphism, and why is `chorus` a good example?
5. When would you use composition instead of inheritance?

**Part 2 done when**
- [ ] `D3 P2 OK` prints
- [ ] You wrote the five answers above
- [ ] You can say the three sentences from the top of this file

---

# Part 3 · Errors and exceptions (50 min)

### 3.1 What an exception is
When something goes wrong, Python creates an **exception**: an error object. It interrupts the normal flow and **travels up** through the functions that called each other. If **nobody catches it**, the program stops and prints a **traceback**. If something up the chain **catches** it (with `try/except`), the program carries on.

### 3.2 Reading a traceback (do this *every* time)
```
Traceback (most recent call last):
  File "app.py", line 12, in <module>
    report(users)
  File "app.py", line 8, in report
    return total / count
           ~~~~~~^~~~~~~
ZeroDivisionError: division by zero
```
**Read it from the bottom up:**
1. **Last line:** the error **type** and **message**: `ZeroDivisionError: division by zero`. *What* happened.
2. **The line just above it:** the exact line that failed: `return total / count`, in function `report`, `app.py` line 8. *Where* it happened.
3. Lines further up: **who called whom** (`line 12` called `report`). *How we got there.*

You don't need to understand everything in it. **Find the type, the message, and the last line of *your* code.**

### 3.3 `try` / `except` / `else` / `finally`
```python
try:
    value = int(text)                 # code that might fail
except ValueError:
    print("not a number")             # runs ONLY if a ValueError happened
else:
    print("converted OK")             # runs ONLY if nothing went wrong
finally:
    print("always runs")              # ALWAYS, error or not (cleanup)
```
Walk it with two inputs:

| `text` is | what runs |
|---|---|
| `"42"` | `try` → `else` → `finally` |
| `"hi"` | `try` (fails at `int`) → `except ValueError` → `finally` |

Rules:
- **Catch the narrowest exception you can handle:** `except ValueError`, not a bare `except:` or `except Exception: pass`. Hiding errors makes bugs invisible.
- Catch several: `except (ValueError, TypeError):`. Keep the error object with `as`: `except ValueError as err:` then `str(err)`.
- Python checks `except` blocks **in order** and runs the **first match**.
- `finally` runs even when `return` or an uncaught error happens (that's what it's for: closing files, releasing resources).

The common built-in exceptions: `ValueError` (right type, bad value: `int("x")`), `TypeError` (wrong type: `1 + "a"`), `KeyError` (missing dict key), `IndexError` (list index too big), `FileNotFoundError`, `ZeroDivisionError`, `AttributeError` (no such attribute).

### 3.4 Raising your own errors
```python
def withdraw(balance: float, amount: float) -> float:
    if amount > balance:
        raise ValueError("insufficient funds")      # you signal the problem
    return balance - amount
```
**When to `return None` vs `raise`:**
- Return `None` only when "nothing" is a **normal, expected** answer (*"find user by email"* → none found).
- **Raise** when something is **wrong** and the caller should deal with it. Raising can't be silently ignored; `None` can, and then crashes later somewhere confusing.

### 3.5 Your own exception types
```python
class AppError(Exception):
    """Base class for all our errors."""

class NotFound(AppError):
    pass

class ValidationError(AppError):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")      # (that's inheritance again!)
        self.field = field
        self.message = message
```
Why a **base class**? Anyone can then catch *all your errors* with `except AppError:`, or just one kind with `except NotFound:`. Extra attributes (`field`) let the code that catches it react precisely.

### 3.6 Chaining: `raise … from …`
```python
try:
    return users[user_id]
except KeyError as exc:
    raise NotFound(f"user {user_id} not found") from exc
```
This raises your **meaningful** error but keeps the original one attached as `__cause__`, so the full story survives in the traceback.

### 3.7 Python's style: "ask forgiveness, not permission"
Often it's cleaner to **try it and handle the failure** than to check everything first:
```python
try:
    age = int(text)
except ValueError:
    ...
```
(But don't wrap huge blocks in `try`; keep the `try` body small.)

### 3.8 `assert` is not for users' mistakes
`assert condition` is a **developer sanity check** ("this must be true, or my code is wrong"). It can be switched off. For **bad user input or runtime problems, `raise`** a proper exception. (Our self-check lines use `assert` because they are developer checks.)

### 3.9 `with`: cleanup you can't forget
```python
with open("notes.txt", encoding="utf-8") as f:
    text = f.read()
# the file is closed here, even if an error happened inside the block
```
`with` guarantees the cleanup. (In Module 1 Day 4 you'll write your own, and see it's exactly how FastAPI opens and closes a database session.)

### 3.10 How this looks in your backend (a preview)
Your business code **raises domain errors**; the web layer **translates them into HTTP status codes**:
```python
try:
    project = get_project(session, 7)
except NotFound as err:
    raise HTTPException(status_code=404, detail=str(err))
```
Next week you'll make that translation happen **in one place** for every error.

### Type it → `drills/d3_p3_errors.py`
Type the examples in 3.3, 3.4, 3.5 and 3.6. Then **cause** a `KeyError`, an `IndexError` and a `ZeroDivisionError` with no `try`, and read each traceback aloud (type, message, which line).

### Read these tracebacks (no code needed)
For each: what is the **error type**, **what went wrong**, and **which line of your code**?
```
# T1
Traceback (most recent call last):
  File "shop.py", line 9, in <module>
    print(prices["milk"])
KeyError: 'milk'

# T2
Traceback (most recent call last):
  File "shop.py", line 5, in total
    return sum(items) / len(items)
ZeroDivisionError: division by zero
```
(Answers at the bottom.)

### Predict the output (guess first)
```python
# P9
def f():
    try:
        return "try"
    finally:
        print("finally")
print(f())

# P10
try:
    int("x")
except ValueError:
    print("A")
except Exception:
    print("B")
else:
    print("C")
finally:
    print("D")

# P11
try:
    print(1)
except Exception:
    print("x")
else:
    print(2)
finally:
    print(3)
```

### Exercises: Part 3
(imports at the top of the file: `import json`, `from pathlib import Path`)
7. **`safe_int(text, default: int | None = None) -> int | None`**: return the int, or `default` if conversion fails (handle **both** `ValueError` and `TypeError`).
8. **`class ValidationError(Exception)`** with `__init__(self, field: str, message: str)`: `str(err)` is `"age: must be positive"`, and `err.field` exists. Then **`validate_user(data: dict) -> dict`**: `name` must be a non-blank string (after stripping); `age` must be an **`int`** from 0 to 150. **Check `name` first.** Raise `ValidationError(field, message)`; return `data` unchanged if valid.
9. **`class ConfigError(Exception)`** and **`load_config(path: Path) -> dict`**: a missing file or invalid JSON must raise `ConfigError(...)` **`from`** the original error.

**Self-check**
```python
assert safe_int("42") == 42
assert safe_int("4x2") is None
assert safe_int("oops", default=-1) == -1
assert safe_int(None) is None

err = ValidationError("age", "must be positive")
assert str(err) == "age: must be positive" and err.field == "age"
good = {"name": "Asha", "age": 30}
assert validate_user(good) == good
cases = [
    ({"age": 30}, "name"),
    ({"name": "  ", "age": 30}, "name"),
    ({"name": "A", "age": -1}, "age"),
    ({"name": "A", "age": "30"}, "age"),
    ({"name": "A"}, "age"),
]
for bad, field_name in cases:
    try:
        validate_user(bad)
    except ValidationError as e:
        assert e.field == field_name, (bad, e.field)
    else:
        raise AssertionError(f"no error for {bad}")

Path("scratch").mkdir(exist_ok=True)
Path("scratch/bad.json").write_text("{not json", encoding="utf-8")
Path("scratch/good.json").write_text('{"debug": true}', encoding="utf-8")
assert load_config(Path("scratch/good.json")) == {"debug": True}
assert raises(ConfigError, load_config, Path("scratch/bad.json"))
try:
    load_config(Path("scratch/nope.json"))
except ConfigError as e:
    assert isinstance(e.__cause__, FileNotFoundError)
else:
    raise AssertionError("expected ConfigError")
print("D3 P3 OK")
```

**Part 3 done when**
- [ ] `D3 P3 OK` prints
- [ ] You can read a traceback from the bottom up
- [ ] You can explain `else` vs `finally`, and when to raise vs return `None`

---

# Part 4 · Modules, packages, imports (35 min)

### 4.1 Modules and packages
- A **module** is **one `.py` file**. `text_tools.py` is a module.
- A **package** is a **folder containing an `__init__.py` file** (it can be empty). It groups modules. That is all your future `app/` folder will be.

### 4.2 Importing
```python
import math                          # use as math.pi
from pathlib import Path             # use as Path(...)
import json as js                    # a nickname (rare)
from .text_tools import slugify      # relative import: "from my sibling module"
from pkgdrill.text_tools import slugify   # absolute import: full path from the project root
```
Avoid `from x import *`; you can't tell where names come from.

Python finds modules by searching the **current project folder** and the **installed packages** (the `.venv` that `uv` manages). That's why we always **run commands from the project root** (`python-fundamentals/`).

### 4.3 Running code: `python file.py` vs `python -m package.module`
- `python pkgdrill/main.py` runs the file **as a loose script**. Python doesn't know it belongs to a package, so **relative imports (`from .x import y`) break**.
- `python -m pkgdrill.main` runs it **as part of the package**: relative imports work. **This is how you run package code.** (With uv: `uv run python -m pkgdrill.main`.)

### 4.4 `if __name__ == "__main__":`
Every module has a built-in name `__name__`.
- When you **run** the file (`python -m pkgdrill.main`), `__name__` is `"__main__"`.
- When another module **imports** it, `__name__` is the module's own name.

So this block runs **only when the file is the one being run**, not when it's imported:
```python
if __name__ == "__main__":
    print("running as a program")
```
Put "start-up" code there so that importing a module doesn't trigger it.

### 4.5 Circular imports, and how to avoid them
If `a.py` imports `b.py` and `b.py` imports `a.py`, Python hits a loop and crashes. The fix is **layering**: imports should only flow **one way (downwards)**. In your FastAPI app:
```
routers  ──▶  services  ──▶  models
   │             │
   └──▶ schemas ◀┘            (nobody imports routers; models don't import services)
```
If two modules need the same thing, move that thing into a **third** module both import.

### 4.6 Settings, secrets, and environment variables
Never write passwords or secrets in code (it ends up in Git). Read them from the **environment**:
```python
import os
db_url = os.environ.get("DATABASE_URL", "sqlite:///dev.db")   # a default if it's not set
```
In your backend you'll use a `.env` file plus a library (`pydantic-settings`) that does this neatly.

### 4.7 What uv does, in four lines
- `pyproject.toml` = what your project **needs** (its dependencies).
- `uv.lock` = the **exact versions** installed.
- `.venv/` = the **installed copy** (a private Python for this project; never commit it).
- `uv add <package>` installs one; `uv run <command>` runs a command inside that environment.

### Build → the `pkgdrill` package
In `python-fundamentals/` create this (all names exactly):
```
pkgdrill/
├── __init__.py        (empty)
├── geometry.py
├── text_tools.py
└── main.py
pkgdrill_check.py      (next to the pkgdrill folder, NOT inside it)
```
- **`geometry.py`:** `area_circle(radius: float) -> float`, rounded to 2 decimals (`area_circle(5) == 78.54`).
- **`text_tools.py`:** `slugify(text: str) -> str`: lowercase; keep only letters, digits, spaces and hyphens; collapse runs of spaces into single hyphens; trim the ends. (`"  Hello, World! "` → `"hello-world"`.) *Hint: `ch.isalnum()`, a join over `text.lower()`, then `"-".join(...split())`.*
- **`main.py`:** import both with **relative imports**; under `if __name__ == "__main__":` print `slug=hello-world area=78.54` (computed from the two functions, not typed).

**`pkgdrill_check.py`** (type this; it's your self-check)
```python
from pkgdrill.geometry import area_circle
from pkgdrill.text_tools import slugify

assert slugify("  Hello, World! ") == "hello-world"
assert slugify("Python   is   FUN") == "python-is-fun"
assert area_circle(5) == 78.54
assert area_circle(0) == 0.0
print("PKGDRILL OK")
```
Run these three commands from `python-fundamentals/`:
```bash
uv run python pkgdrill_check.py            # PKGDRILL OK
uv run python -m pkgdrill.main             # slug=hello-world area=78.54
uv run python pkgdrill/main.py             # ImportError: read it!
```
- **Expect for the third:** `ImportError: attempted relative import with no known parent package`.
- **Write one sentence in your notes:** why does the second command work and the third fail? *(Answer at the bottom.)*

**Part 4 done when**
- [ ] `PKGDRILL OK` prints and `main` prints `slug=hello-world area=78.54`
- [ ] You can explain why the third command fails
- [ ] You can explain `if __name__ == "__main__":` and why circular imports happen

---

## Wrap-up (10 min)

**1. Explain without notes** (aloud, or 1–2 lines each in your cheat sheet)
1. Class attribute vs instance attribute? What is `self`?
2. What do you get from `@dataclass` for free? Why `default_factory`?
3. When do you use `@classmethod`? Give one real example.
4. What does a child class get from its parent? What is overriding? What is polymorphism?
5. Why a base exception class for your own errors?
6. What does `raise X from e` preserve? What do `else` and `finally` do?
7. Why `python -m pkg.mod` instead of `python pkg/mod.py`? What is `if __name__ == "__main__":` for?
8. In a backend, who raises domain errors and who turns them into HTTP responses?

**2. Cheat sheet:** one line per question in `notes/00-python-cheatsheet.md`: your own words plus the smallest example.

**3. Journal** (`journal.md`): `Did: … / Confused me: … / Tomorrow starts with: …`

**4. Commit and push** (VS Code Source Control: message, **Commit**, **Sync/Push**), or:
```bash
cd ~/backend-journey
git add .
git commit -m "day 3: classes, inheritance, errors, modules"
git push
```

**Tomorrow (Day 4):** decorators, generators and context managers, pytest/debugging/logging, and the async taste (the pieces your FastAPI code is built on). Tell me **"Day 4 please"** plus anything that confused you today.

### Day 3 done when
- [ ] `D3 P1 OK`, `D3 P2 OK`, `D3 P3 OK`, `PKGDRILL OK`
- [ ] The three sentences about inheritance are in your own words in your notes
- [ ] Cheat sheet lines, journal, and commit done

---

# Quick reference (keep this)

```python
class Name(Parent):                       # inherits from Parent
    shared = 0                            # class attribute (shared)
    def __init__(self, x):                # runs when you create an object
        super().__init__(x)               # call the parent's __init__ first
        self.x = x                        # instance attribute
    @property
    def double(self): return self.x * 2   # read-only "attribute"
    @classmethod
    def from_dict(cls, d): return cls(d["x"])   # alternative constructor
    def __repr__(self): return f"Name({self.x!r})"

@dataclass                                # auto __init__/__repr__/__eq__
class Task:
    title: str
    tags: list[str] = field(default_factory=list)

try: ...                                  # might fail
except (ValueError, TypeError) as err: ...# handle it
else: ...                                 # no error
finally: ...                              # always
raise NotFound("msg") from original       # your error, with the cause kept
```
**Rules:** child gets everything from parent · override to change · `super()` for the parent's version · same call, different behaviour = polymorphism · "is-a" → inherit, "has-a" → store an object · catch narrow errors · raise (don't return `None`) when something is wrong · run packages with `python -m pkg.mod` · put start-up code under `if __name__ == "__main__":`

---

# Solutions (open only after 20 minutes of trying one exercise)

Read one, close the file, **retype it from memory**.

### Part 1
```python
from dataclasses import dataclass, field


class BankAccount:
    def __init__(self, owner: str, balance: float = 0) -> None:
        self.owner = owner
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount

    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self._balance})"


@dataclass
class Playlist:
    name: str
    songs: list[str] = field(default_factory=list)


@dataclass
class User:
    name: str
    age: int

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(name=data["name"], age=int(data["age"]))
```

### Part 2
```python
import math


class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "..."


class Dog(Animal):
    def speak(self) -> str:
        return "Woof"


class Cat(Animal):
    def speak(self) -> str:
        return "Meow"


def chorus(animals: list[Animal]) -> list[str]:
    return [f"{a.name}: {a.speak()}" for a in animals]


class Shape:
    def area(self) -> float:
        raise NotImplementedError


class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2


def total_area(shapes: list[Shape]) -> float:
    return sum(s.area() for s in shapes)


class Employee:
    def __init__(self, name: str, salary: int) -> None:
        self.name = name
        self.salary = salary

    def describe(self) -> str:
        return f"{self.name} earns {self.salary}"


class Manager(Employee):
    def __init__(self, name: str, salary: int, reports: list[str] | None = None) -> None:
        super().__init__(name, salary)
        self.reports = reports if reports is not None else []   # never `reports=[]` as the default

    def describe(self) -> str:
        return f"{super().describe()} and manages {len(self.reports)} people"
```

### Part 3
```python
import json
from pathlib import Path


def safe_int(text, default=None):
    try:
        return int(text)
    except (ValueError, TypeError):
        return default


class ValidationError(Exception):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")
        self.field = field
        self.message = message


def validate_user(data: dict) -> dict:
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("name", "must be a non-blank string")
    age = data.get("age")
    if not isinstance(age, int) or not 0 <= age <= 150:
        raise ValidationError("age", "must be an integer from 0 to 150")
    return data


class ConfigError(Exception):
    pass


def load_config(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"config file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config file is not valid JSON: {path}") from exc
```

### Part 4
`pkgdrill/text_tools.py`
```python
def slugify(text: str) -> str:
    kept = "".join(ch for ch in text.lower() if ch.isalnum() or ch in " -")
    return "-".join(kept.split())
```
`pkgdrill/geometry.py`
```python
import math


def area_circle(radius: float) -> float:
    return round(math.pi * radius ** 2, 2)
```
`pkgdrill/main.py`
```python
from .geometry import area_circle
from .text_tools import slugify

if __name__ == "__main__":
    print(f"slug={slugify('  Hello, World! ')} area={area_circle(5)}")
```
**Why the third command fails:** `python pkgdrill/main.py` runs the file as a loose script, so Python doesn't know it belongs to the `pkgdrill` package and can't resolve `from .geometry import …`. `python -m pkgdrill.main` runs it *as part of the package*, so relative imports work.

---

# Answers: predict the output

**Part 1**
- **P1:** `2 2 2`. `count` is a class attribute shared by all objects; every `__init__` bumped the same counter.
- **P2:** `[]`. Each object gets its *own* `items` list (instance attribute).
- **P3:** `2`. `q = p` doesn't copy: both names point at the **same** object.
- **P4:** `True False`. A dataclass compares field by field (`==`), but they are two different objects (`is`).

**Part 2**
- **P5:** `I say ... I say Woof`. `Dog` inherits `intro`, but `intro` calls `self.speak()`, and lookup starts at the object's real class (`Dog`).
- **P6:** `B init` only. `B` defined its own `__init__`, and the parent's isn't called automatically.
- **P7:** `A init` then `C init`. `super().__init__()` called the parent's version first.
- **P8:** `True False True`.

**Part 3**
- **P9:** prints `finally`, then `try`. `finally` runs just before the function actually returns.
- **P10:** prints `A` then `D` (the `int("x")` fails → `except ValueError` runs; `else` is skipped; `finally` always runs).
- **P11:** prints `1`, `2`, `3` (no error: `try` → `else` → `finally`).

**Tracebacks**
- **T1:** `KeyError` (the dict has no key `"milk"`), on line 9 of `shop.py` (`print(prices["milk"])`). Fix: use `prices.get("milk")` or check the key first.
- **T2:** `ZeroDivisionError` (`items` is empty, so `len(items)` is 0), on line 5 in `total` (`return sum(items) / len(items)`). Fix: handle the empty list before dividing.

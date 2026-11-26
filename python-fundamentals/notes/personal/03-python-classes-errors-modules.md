# 03 · Python Classes, Errors, and Modules · Personal Notes

> 🧭 **How to use this note:** Start with the map and the bold lines. Each section stands on its own, so use the contents to revisit one concept at a time. These notes keep the developer-level detail and give extra space to your questions about importing, `__main__`, and what code actually runs.

## 📚 Table of contents

- [60-second map](#60-second-map)
- [1. Classes and objects](#1-classes-and-objects)
- [2. Attributes, methods, and `self`](#2-attributes-methods-and-self)
- [3. Class attributes, properties, and constructors](#3-class-attributes-properties-and-constructors)
- [4. Dataclasses and safe mutable defaults](#4-dataclasses-and-safe-mutable-defaults)
- [5. Inheritance and method lookup](#5-inheritance-and-method-lookup)
- [6. Overriding, `super()`, and polymorphism](#6-overriding-super-and-polymorphism)
- [7. Inheritance vs composition](#7-inheritance-vs-composition)
- [8. Exceptions and tracebacks](#8-exceptions-and-tracebacks)
- [9. Handling and raising errors](#9-handling-and-raising-errors)
- [10. Custom exceptions, chaining, and cleanup](#10-custom-exceptions-chaining-and-cleanup)
- [11. Modules, packages, and imports](#11-modules-packages-and-imports)
- [12. `__name__` and `if __name__ == "__main__"`](#12-__name__-and-if-__name__--__main__)
- [13. Running package code: `-m` vs a file path](#13-running-package-code--m-vs-a-file-path)
- [14. Circular imports and project structure](#14-circular-imports-and-project-structure)
- [15. Environment settings and `uv`](#15-environment-settings-and-uv)
- [Most important doubts, resolved](#most-important-doubts-resolved)
- [One-page recall](#one-page-recall)
- [Recall drill](#recall-drill)

### Visual guide

| Mark | Meaning |
|---|---|
| 🧠 **Remember** | A core fact worth recalling |
| ❓ **Doubt resolved** | A question you asked, with the key distinction |
| ⚠️ **Trap** | An easy-to-make mistake |
| 🔁 **Connection** | How this relates to another concept |
| 🛠️ **Practical** | A code or debugging example |

---

## 60-second map

### Classes

**A class groups data and the operations that work on that data.**  
A **class** is a template; an **object/instance** is one value made from it.

```text
class BankAccount  ──creates──▶  acct = BankAccount(...)
blueprint                         object with its own attributes
```

### Inheritance and polymorphism

1. A **child class gets behavior/data from its parent** unless it replaces it.
2. A child can **override** a parent method.
3. **Polymorphism:** the same method call can behave differently for different object types.

```text
Animal.speak()       Dog.speak() = "Woof"       Cat.speak() = "Meow"
                           \                         /
                            same call: animal.speak()
```

### Errors

**An exception interrupts normal flow and propagates up the call stack until handled.**  
Read a traceback from the **bottom upward**: error type/message first, then the failing line and its callers.

### Modules

**A module is a `.py` file. A package is a folder used to organize modules.**  
Importing a module executes its top-level statements. The `if __name__ == "__main__":` guard is optional and is for code that should run only when that module is the entry point.

---

## 1. Classes and objects

A class bundles related data and behavior. Without one, data and functions can be separated and become easier to misuse:

```python
account = {"owner": "asha", "balance": 100}

def deposit(account: dict, amount: float) -> None:
    account["balance"] += amount
```

A class expresses that an account owns its balance and its account-related behavior:

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

- `BankAccount` is the **class**.
- `acct` is an **instance/object**.
- You can create many accounts; each object has its own instance data.

Classes appear in backend code as Pydantic models, ORM models, settings objects, services, and custom exceptions. Not everything in a backend must be a class; use one when it makes the data/behavior relationship clearer.

---

## 2. Attributes, methods, and `self`

### What happens when an object is made?

For `acct = BankAccount("asha", 100)`:

1. Python creates a new object.
2. Python calls `BankAccount.__init__` with that object and the supplied arguments.
3. Inside `__init__`, `self` refers to that new object.
4. Assignments such as `self.owner = owner` store attributes on the object.
5. The resulting object is assigned to `acct`.

`__init__` initializes a newly created object. It is not the method that creates the object itself.

### What is `self`?

`self` is the conventional name for the current instance. It is the first parameter of an instance method. Python supplies it when a method is called through an object:

```python
acct.deposit(50)
```

is conceptually equivalent to:

```python
BankAccount.deposit(acct, 50)
```

You normally do not pass `self` manually.

### Attributes vs methods

- **Attribute:** data associated with an object, e.g. `self.owner`.
- **Method:** a function defined in a class, e.g. `deposit`.
- `acct.deposit` refers to the method; `acct.deposit(50)` calls it.
- `_balance` uses a leading underscore to signal “internal use by convention.” It is not a strict access lock.

### `__repr__`

`__repr__` provides a useful developer-facing representation:

```python
def __repr__(self) -> str:
    return f"BankAccount(owner={self.owner!r}, balance={self._balance})"
```

Then `repr(acct)` or `print(acct)` is more informative than a default address-like representation.

---

## 3. Class attributes, properties, and constructors

### Instance attribute vs class attribute

```python
class Counter:
    count = 0                       # class attribute: shared on the class

    def __init__(self) -> None:
        Counter.count += 1
        self.id = Counter.count     # instance attribute: belongs to this object
```

- **Instance attribute:** each object has its own value, usually assigned through `self`.
- **Class attribute:** defined on the class and shared unless shadowed on an instance.

⚠️ A mutable class attribute such as `items = []` is one shared list. It does **not** make a fresh list for each object.

### `@property`

A property exposes a method using attribute syntax:

```python
class BankAccount:
    def __init__(self, balance: float) -> None:
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance


acct.balance       # read the value; no parentheses
acct.balance = 5   # AttributeError if no setter exists
```

A read-only property lets callers inspect a value while requiring changes to go through methods such as `deposit` and `withdraw`, where validation can happen.

### `@classmethod` as an alternative constructor

A normal instance method receives `self`. A class method receives `cls`, the class:

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(name=data["name"], age=int(data["age"]))


user = User.from_dict({"name": "Asha", "age": "30"})
```

`cls(...)` builds an instance of the class. This is useful when input comes in a different format and must be converted before constructing an object. It also works well with subclasses because `cls` is the class on which the method was called.

`@staticmethod` defines a function in a class namespace without automatic `self` or `cls`; use it only when keeping the helper with the class improves organization.

---

## 4. Dataclasses and safe mutable defaults

Use a dataclass when a class mainly stores data:

```python
from dataclasses import asdict, dataclass, field


@dataclass
class Task:
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)
```

By default, `@dataclass` generates methods including:

- `__init__`
- `__repr__`
- `__eq__` (field-by-field equality)

```python
t = Task("write code")
repr(t)                         # Task(title='write code', done=False, tags=[])
t == Task("write code")         # True: values match
t is Task("write code")         # False: distinct objects
asdict(t)                       # {'title': 'write code', 'done': False, 'tags': []}
```

`field(default_factory=list)` calls `list()` separately for every instance, so each gets a fresh list.

⚠️ Do not write a mutable dataclass default like `tags: list[str] = []`. Shared mutable state between instances is usually a bug. Use `default_factory`.

**Rule of thumb:** dataclass for data containers; a regular class when the object has substantial behavior or invariants.

---

## 5. Inheritance and method lookup

### The “is-a” relationship

Inheritance lets a child class reuse and specialize a parent (base/super) class:

```python
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "..."

    def intro(self) -> str:
        return f"{self.name} says {self.speak()}"


class Dog(Animal):
    def speak(self) -> str:
        return "Woof"


class Cat(Animal):
    def speak(self) -> str:
        return "Meow"
```

`Dog(Animal)` means `Dog` derives from `Animal`. `Dog` has no `__init__` or `intro`, so it inherits those methods.

```python
rex = Dog("Rex")
rex.name       # "Rex", initialized using Animal.__init__
rex.intro()    # "Rex says Woof"
```

### How `rex.intro()` finds the methods

To find `intro`, Python looks through the method resolution order (MRO):

```text
Dog → Animal → object
```

`Dog` has no `intro`, so Python finds `Animal.intro`. That implementation calls `self.speak()`. Here `self` is still the `Dog` instance `rex`, so Python looks for `speak` starting from `Dog` and finds `Dog.speak`.

**Key insight:** an inherited method still receives the actual child object as `self`. Calls it makes can therefore dispatch to the child’s overridden methods.

```python
Dog.__mro__   # (Dog, Animal, object)
```

### `isinstance` and `issubclass`

```python
isinstance(rex, Dog)             # True
isinstance(rex, Animal)          # True: a Dog is an Animal
isinstance(Animal("x"), Dog)     # False
issubclass(Dog, Animal)          # True
```

---

## 6. Overriding, `super()`, and polymorphism

### Overriding

When a child defines a method with the same name as a parent method, the child’s implementation is used for child objects. This is **overriding**:

```python
Animal("x").speak()   # "..."
Dog("Rex").speak()    # "Woof"
```

### `super()`

Use `super()` to call the next implementation in the method resolution order—commonly the parent’s method:

```python
class Employee:
    def __init__(self, name: str, salary: int) -> None:
        self.name = name
        self.salary = salary

    def describe(self) -> str:
        return f"{self.name} earns {self.salary}"


class Manager(Employee):
    def __init__(
        self,
        name: str,
        salary: int,
        reports: list[str] | None = None,
    ) -> None:
        super().__init__(name, salary)
        self.reports = reports if reports is not None else []

    def describe(self) -> str:
        return f"{super().describe()} and manages {len(self.reports)} people"
```

- `super().__init__(name, salary)` initializes the inherited `name` and `salary`.
- `super().describe()` reuses the parent’s description and extends it.

⚠️ If a child defines its own `__init__`, Python does **not** automatically run the parent’s `__init__`. Forgetting `super().__init__(...)` can leave parent attributes unset.

### Polymorphism

**Polymorphism means one common operation can produce type-specific behavior.** The caller uses the same method name and does not need to branch on each concrete class:

```python
def chorus(animals: list[Animal]) -> list[str]:
    return [f"{animal.name}: {animal.speak()}" for animal in animals]


chorus([Dog("Rex"), Cat("Tom"), Animal("Generic")])
# ["Rex: Woof", "Tom: Meow", "Generic: ..."]
```

`chorus` does not need `if isinstance(..., Dog)` or `elif ... Cat`. If a `Cow(Animal)` provides its own `speak`, the same function can use it without modification.

Backend-shaped example:

```python
class Notifier:
    def send(self, message: str) -> None:
        raise NotImplementedError


class EmailNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"emailing: {message}")


class SmsNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"texting: {message}")


def alert_all(notifiers: list[Notifier], message: str) -> None:
    for notifier in notifiers:
        notifier.send(message)
```

The base class defines a common interface; each child supplies its behavior. `NotImplementedError` is one way to signal that the base method is a template. Python also has the `abc` module for formal abstract base classes.

**The three sentences to retain:**

1. A child class inherits behavior and attributes from its parent.
2. The child can override a parent method.
3. Code using the parent interface can work with children; the same call can do different things (polymorphism).

### Where inheritance appears in backend code

- `class Project(BaseModel)` inherits validation and serialization behavior from Pydantic.
- `class Project(Base)` may inherit ORM behavior from a database framework.
- `class NotFound(AppError)` specializes an application error.
- `class AppError(Exception)` makes custom errors part of Python’s exception hierarchy.

---

## 7. Inheritance vs composition

Use the **is-a test**:

- A Dog **is an** Animal → inheritance may fit.
- A Car **has an** Engine → composition fits.

```python
class Engine:
    ...


class Car:
    def __init__(self) -> None:
        self.engine = Engine()
```

**Composition** means an object holds another object as an attribute. Prefer composition by default when the relationship is “has-a.” Use inheritance for genuine specialization and framework-required base classes. Avoid deep inheritance chains and inheriting only to copy a few lines.

---

## 8. Exceptions and tracebacks

### What is an exception?

An exception is an error object that interrupts normal execution. It propagates up through the functions that called the failing code. If nobody handles it, the program stops and Python prints a traceback.

### Read tracebacks from the bottom up

```text
Traceback (most recent call last):
  File "app.py", line 12, in <module>
    report(users)
  File "app.py", line 8, in report
    return total / count
ZeroDivisionError: division by zero
```

Read bottom-up:

1. **Last line:** exception type and message — what happened.
2. **Nearest preceding frame:** the failing line in your code — where it happened.
3. **Frames above:** the call path — how execution reached it.

You do not need to decode every frame immediately. First find the exception type/message and the relevant line in your own code.

Common built-in exceptions:

| Exception | Typical cause |
|---|---|
| `ValueError` | Correct kind of value expected, but the value is invalid: `int("x")` |
| `TypeError` | Operation or function receives an inappropriate type: `1 + "a"` |
| `KeyError` | Dictionary key is absent |
| `IndexError` | List/sequence index is out of range |
| `FileNotFoundError` | Requested file does not exist |
| `ZeroDivisionError` | Division by zero |
| `AttributeError` | Object has no requested attribute |

---

## 9. Handling and raising errors

### `try`, `except`, `else`, `finally`

```python
try:
    value = int(text)
except ValueError as err:
    print(f"not a number: {err}")
else:
    print("converted OK")
finally:
    print("always runs")
```

| Block | Runs when |
|---|---|
| `try` | First; contains the operation that may fail |
| `except` | A matching exception occurs in `try` |
| `else` | `try` completes without an exception |
| `finally` | Cleanup; runs whether the operation succeeds or fails |

For `text == "42"`: `try` → `else` → `finally`.  
For `text == "hi"`: `try` fails → matching `except` → `finally`; `else` is skipped.

`finally` still runs when returning or when an uncaught exception propagates, which makes it useful for cleanup. A `return` in `finally` can override an earlier return or suppress an exception; avoid returning from `finally`.

### Catch narrowly

```python
try:
    value = int(text)
except (ValueError, TypeError) as err:
    ...
```

- Catch the narrowest exceptions you can reasonably handle.
- Several types can be caught as a tuple.
- `as err` binds the exception object.
- Python checks `except` clauses in order and runs the first matching handler.
- Avoid bare `except:` and `except Exception: pass`; broad silent handling hides bugs.
- Keep the `try` block small so you do not accidentally catch an unrelated failure.

### Return `None` or raise?

- Return `None` when “no result” is a normal, expected outcome, e.g. a search that found no matching user.
- Raise an exception when something is wrong and the caller should handle the failure.

An error represented as `None` can be ignored and cause a confusing failure later. Raise a meaningful exception for invalid input or failed operations.

### `assert` is for developer checks

`assert condition` checks an assumption during development/tests. Assertions can be disabled with optimized Python execution, so do not use them to validate user input or enforce runtime security. Raise an appropriate exception instead.

---

## 10. Custom exceptions, chaining, and cleanup

### Custom exception classes

```python
class AppError(Exception):
    """Base class for application errors."""


class NotFound(AppError):
    pass


class ValidationError(AppError):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")
        self.field = field
        self.message = message
```

Because `NotFound` and `ValidationError` inherit from `AppError`, code can catch all domain-specific errors with `except AppError`, or handle a specific type with `except NotFound`.

Custom attributes such as `.field` let callers respond precisely. `super().__init__(...)` initializes the base `Exception` message, so `str(err)` is useful.

Example validation behavior:

```python
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
```

The order is deliberate: check `name` first, then `age`. Returning the original mapping when valid preserves the input; raising a field-specific exception makes the failure explicit and actionable.

### Translate low-level errors and preserve their cause

```python
try:
    user = users[user_id]
except KeyError as exc:
    raise NotFound(f"user {user_id} not found") from exc
```

`raise NewError(...) from original` presents an error meaningful to the caller while retaining the original exception as `__cause__` and in the traceback.

For example, `load_config(path)` can translate `FileNotFoundError` or `json.JSONDecodeError` into a domain-specific `ConfigError`, using `raise ConfigError(...) from exc`. The caller gets a stable configuration error while the original cause remains inspectable.

In a backend, business/domain code can raise `NotFound`; the web layer can translate it to an HTTP `404`. Keeping this translation at a boundary avoids mixing domain logic with HTTP details.

### `with` for reliable cleanup

```python
with open("notes.txt", encoding="utf-8") as file:
    text = file.read()
# file is closed here, even if an error occurred inside the block
```

The context manager performs cleanup on exit. Use it for resources such as files and database sessions.

---

## 11. Modules, packages, and imports

### Definitions

- **Module:** one Python `.py` file, e.g. `text_tools.py`.
- **Package:** a directory that groups modules. A regular package commonly contains `__init__.py` (which may be empty).

Example:

```text
pkgdrill/
├── __init__.py
├── geometry.py
├── text_tools.py
└── main.py
```

Here `geometry.py`, `text_tools.py`, and `main.py` are modules inside the `pkgdrill` package.

### Import styles

```python
import math
math.pi

from pathlib import Path
Path("file.txt")

import json as js
js.loads("{}")

from .text_tools import slugify
from pkgdrill.text_tools import slugify
```

- `import math`: bind module name; access `math.pi`.
- `from pathlib import Path`: bind a selected name directly.
- `import json as js`: alias the imported module.
- `from .text_tools ...`: relative import from a sibling module, requiring package context.
- `from pkgdrill.text_tools ...`: absolute import from the package root.

Avoid `from x import *`; it obscures where names came from and can introduce collisions.

Python searches import locations such as the current project and installed packages. Run project commands from the project root so package imports resolve predictably.

---

## 12. `__name__` and `if __name__ == "__main__"`

### What is `__name__`?

`__name__` is a module-level variable Python sets to identify how that module is being used:

- When a module is the program entry point, Python sets its `__name__` to `"__main__"`.
- When a module is imported under its package/module name, it gets that name, e.g. `"pkgdrill.main"`.

**`__main__` is not a filename and not a function name.** It is a special module name Python uses for the entry-point module.

### The guard

```python
def start() -> None:
    print("Application started")


if __name__ == "__main__":
    start()
```

The `if` statement is ordinary conditional code. It runs the enclosed startup code only when this module is the entry point; it skips that block when the module is imported under its regular module name.

### The guard is optional

You do **not** need `if __name__ == "__main__":` in every file.

- A tiny script that will never be imported may not need it.
- A reusable module that also has a command-line/startup behavior benefits from it.
- A file that only defines reusable functions/classes may not need any guarded startup code.

Use the guard when a file has both responsibilities: **provide reusable definitions** and **act as a runnable program**.

### Filename does not decide the value

Given a package:

```text
pkgdrill/
├── __init__.py
├── main.py
└── app.py
```

Running a module as the entry point gives it `"__main__"` regardless of the filename:

```bash
uv run python -m pkgdrill.main
uv run python -m pkgdrill.app
```

In either case, the module being executed has `__name__ == "__main__"`. `main.py` has no magical status because of the name `main`.

If another module imports `pkgdrill.main`, that imported module's `__name__` is `"pkgdrill.main"`; its `if __name__ == "__main__":` block is false.

---

## 13. Running package code: `-m` vs a file path

### `python -m package.module`

```bash
uv run python -m pkgdrill.main
```

Python locates `pkgdrill.main` as a module and executes it as the program entry point. Its `__name__` is `"__main__"`, while package context is available, so relative imports such as `from .geometry import area_circle` work.

### `python path/to/file.py`

```bash
uv run python pkgdrill/main.py
```

Python executes `main.py` as a loose script. It is still the entry point (`__name__ == "__main__"`), but it does not have the same package context; a relative import such as `from .geometry import ...` fails with:

```text
ImportError: attempted relative import with no known parent package
```

### Keep the two facts separate

> ❓ **Why does the `-m` command both set `__name__` to `"__main__"` and allow relative imports?**  
> `__name__` answers “is this the entry point?” Package metadata/context separately tells Python where relative imports start. `-m` supplies package context while executing the selected module as the entry point.

The same module can therefore have:

```text
__name__    = "__main__"       # entry-point identity
__package__ = "pkgdrill"       # package context for relative imports
```

Exact runtime metadata can vary with execution form; the important practical rule is to run package modules using `python -m package.module` from the project root.

### Demonstration

`pkgdrill/main.py`:

```python
from .geometry import area_circle
from .text_tools import slugify

if __name__ == "__main__":
    print(f"slug={slugify('  Hello, World! ')} area={area_circle(5)}")
```

Run:

```bash
uv run python -m pkgdrill.main
```

It prints the computed values and resolves sibling relative imports. Running `uv run python pkgdrill/main.py` treats the file as a loose script and fails on the relative imports.

---

## 14. Circular imports and project structure

A circular import occurs when, for example, `a.py` imports `b.py` and `b.py` imports `a.py`. During module initialization Python can encounter a partially initialized module, causing missing-name/import errors or fragile behavior.

Prefer one-way dependency flow (“layering”):

```text
routers  ──▶  services  ──▶  models
   │             │
   └──▶ schemas ◀┘
```

The exact architecture varies, but avoid modules that need each other to initialize. If two modules need the same definition, move that definition into a third module both can import. Keep lower-level modules from importing higher-level application layers.

---

## 15. Environment settings and `uv`

### Environment variables and secrets

Do not hard-code passwords or secrets in source code; source may be committed or shared. Read sensitive configuration from environment variables or a suitable secret manager:

```python
import os

db_url = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
```

The fallback shown is for local development; production secrets should be configured securely. A `.env` file plus a settings library such as `pydantic-settings` is a common development workflow, with the file kept out of version control when it contains secrets.

### `uv` project files

| Item | Purpose |
|---|---|
| `pyproject.toml` | Project metadata and declared dependencies |
| `uv.lock` | Locked dependency versions/resolution |
| `.venv/` | Project-specific installed environment; normally not committed |
| `uv add <package>` | Add a dependency |
| `uv run <command>` | Run a command in the project environment |

---

## Most important doubts, resolved

1. **Is `__main__` the filename or a function?** No. It is the special value Python assigns to `__name__` for the module executed as the entry point.
2. **Does the file have to be named `main.py`?** No. `python -m pkgdrill.app` makes `pkgdrill.app` the entry point too; its `__name__` is `"__main__"`.
3. **What does `__name__` become when a module is imported?** Its normal module name, e.g. `"pkgdrill.main"` or `"app"`, not `"__main__"`.
4. **Is `if __name__ == "__main__":` mandatory?** No. It is optional and useful when a module should be importable without running its startup behavior.
5. **What happens when a file is imported?** Python executes its top-level statements to initialize the module. Function and class definitions are created, and top-level calls/prints/assignments execute.
6. **Do function bodies run just because a function is defined during import?** No. Defining the function creates a function object; its body runs only when it is called. (Decorators and default argument expressions are evaluated while the definition executes.)
7. **Does `if __name__ == "__main__":` stop all code from running on import?** No. It only prevents the statements indented inside that particular `if` block from running. Other top-level statements still run.
8. **Does importing the same module repeatedly rerun its top-level code?** Normally, no: Python caches imported modules in `sys.modules` within that interpreter. Explicit reloads and separate processes are different cases.
9. **Why does `python -m pkgdrill.main` work with relative imports?** It executes the module in package context. Running `python pkgdrill/main.py` as a loose script does not provide the same relative-import context.
10. **Why can `__name__` be `"__main__"` while relative imports still work?** Entry-point identity and package context are separate pieces of metadata; `-m` sets up package context while executing the module as the entry point.
11. **Does a child class automatically call the parent's `__init__` if it defines its own?** No. Call `super().__init__(...)` when parent initialization is needed.
12. **What does polymorphism mean here?** Call one shared method on objects of different child types; each object's implementation supplies its behavior without type-checking branches.
13. **What is the difference between overriding and polymorphism?** Overriding is a child replacing a method. Polymorphism is the broader ability to use different object types through a common interface and get the appropriate behavior.
14. **When should I inherit vs compose?** Use inheritance for an “is-a” relationship; use composition for “has-a.”
15. **When should I return `None` vs raise?** `None` for an expected absence; raise when an operation failed or input is invalid and the caller should handle the error.

---

## One-page recall

| Topic | Recall sentence |
|---|---|
| Class | Blueprint grouping related data and behavior |
| Instance | One object created from a class |
| `self` | The current instance, passed automatically to instance methods |
| `__init__` | Initializes an already-created instance |
| Instance attribute | Per-object state, usually `self.value` |
| Class attribute | Shared class-level value; beware shared mutable values |
| Property | Method accessed like an attribute |
| Class method | Receives `cls`; useful as an alternative constructor |
| Dataclass | Generates common data-container methods |
| `default_factory` | Creates a fresh mutable default for each instance |
| Inheritance | Child specializes/reuses a parent (“is-a”) |
| Override | Child supplies a method with the same name |
| `super()` | Call the next method implementation in the MRO |
| Polymorphism | Same interface/call, behavior varies by object |
| Composition | One object contains/uses another (“has-a”) |
| Exception | Error object interrupts normal flow and propagates |
| Traceback | Read bottom-up: type/message, failing line, callers |
| `else` in try | Runs only if `try` had no exception |
| `finally` | Cleanup block that runs on success or failure |
| `raise ... from ...` | Raise a useful error while preserving its cause |
| Module | One `.py` file |
| Package | Directory organizing modules; regular packages commonly have `__init__.py` |
| Import | Executes module top-level code on first import in a process |
| Function definition | Creates function; body runs only when called |
| `__name__` | `"__main__"` for entry-point module; normal module name when imported |
| Main guard | Optional gate for startup code; not based on filename |
| `python -m` | Run module with package context |

---

## Recall drill

Try without looking. If an answer is missing, revisit only its section.

1. Explain class vs instance, and what `self` refers to.
2. What does `__init__` do? Is it the object-creation mechanism?
3. Distinguish an instance attribute from a class attribute.
4. Why is `field(default_factory=list)` needed?
5. Describe inheritance, overriding, `super()`, and polymorphism.
6. Why can `Animal.intro()` call a `Dog`'s `speak()` implementation?
7. When is composition a better fit than inheritance?
8. How do you read a traceback?
9. What is the difference between `except`, `else`, and `finally`?
10. When should a function return `None`, and when should it raise?
11. What does `raise ConfigError(...) from exc` preserve?
12. What runs when a module is imported? Do function bodies execute automatically?
13. Is the main guard required? Does the filename have to be `main.py`?
14. Why does `python -m pkgdrill.main` support relative imports but `python pkgdrill/main.py` does not?
15. Explain why `__name__` can be `"__main__"` and relative imports can still work.

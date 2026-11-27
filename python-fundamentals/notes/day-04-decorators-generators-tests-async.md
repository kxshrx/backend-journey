# Day 4: Python the frameworks run on: decorators, generators, tests, async

> Module 1, Day 4 of 30 · about 4 hours including breaks · written for a **Mac**
> **Everything you need for today is in this file.** Don't look anything else up.
> Save it as `notes/days/day-04.md` in your `backend-journey` repo.

---

## Read this first

Today's topics are the Python tricks that **FastAPI itself is built from**:

| Today's idea | Where you'll meet it |
|---|---|
| Decorators | `@app.get("/projects")` |
| Generators and `yield` | the `get_db` dependency |
| Context managers (`with`) | `with SessionLocal() as session:` |
| pytest | every test you'll write from Week 3 |
| Debugging and logging | every bug you'll ever have |
| async / await | Month 2 (today is a 15-minute taste) |

**It's a big day, and you're doing it right after a busy stretch at work. Listen to your energy.** The parts are in priority order. If you run out of steam:
- **Must do:** Part 0 → Part 1 → Part 2. (These are what FastAPI uses directly.)
- **Can slip to the Day 6 buffer:** Part 3 (tests, debugging, logging) and Part 4 (async).
- **Floor rule (zero-energy day):** Part 1 alone counts as a day.

---

## How today works

| Part | Time | What |
|---|---|---|
| Check-in | 5 min | **Recall** 3 things from yesterday without looking; write "today I'm done when…" in `journal.md` |
| **Part 0** | 20 min | Exceptions rescue (the bit that wasn't clear) |
| **Part 1** | 45 min | Functions as values, closures, **decorators** |
| Break | 5 min | Walk, water |
| **Part 2** | 40 min | Iterators, **generators**, **context managers** |
| Break | 10 min | Eat something |
| **Part 3** | 45 min | **pytest**, debugging, logging |
| **Part 4** | 15 min | **async**: see it once |
| Wrap-up | 10 min | Questions, cheat sheet, commit |

**How the exercises work** (same as yesterday)
- Put code in `python-fundamentals/drills/` (file names are given). Run from the `python-fundamentals` folder: `uv run python drills/<file>.py`.
- Exercise blocks end with `assert` lines. If your code is right, nothing happens and the last line prints `OK`. If not, you'll see `AssertionError` with a line number: fix **your code**, never the asserts.
- **Predict the output:** write your guess *first*, then run it. Wrong guesses are where the learning is: one sentence in `notes/00-python-cheatsheet.md` for each miss. Answers are at the bottom.
- **Stuck?** 5 minutes → write `TODO` in your journal and move on · 20 minutes → ask an AI for a *hint* using the prompt in `01-fastapi-start-here.md` · **Solutions are at the bottom**: read one only after 20 minutes of trying, then close the file and retype it from memory.

Paste this helper at the top of every drill file today:
```python
def raises(exc_type, fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except exc_type:
        return True
    return False
```

---

# Part 0 · Exceptions rescue (20 min)

*If your video made exceptions click, skim this and do the quiz at the end as a check. If not, this is a second angle on the same idea. Nothing else is needed.*

### 0.1 The mental model: a hot potato thrown up the stairs
Functions call other functions, like boxes stacked in a tower: `f` calls `g`, `g` calls `h`.
```
main
 └─ f()        ← (3) f has a try/except: it catches the potato here
     └─ g()    ← (2) g can't handle it: throws it up to f
         └─ h()  ← (1) h raises an error: it can't continue
```
- When `h` **raises** an exception, `h` **stops immediately** (its remaining lines never run). The exception is thrown up to whoever called `h`.
- If that function doesn't catch it, **it stops too**, and the exception goes up again.
- This continues **until some `try/except` catches it**. If nobody does, the program ends and prints the **traceback**: the path the potato travelled.

Trace this (type it into `drills/d4_p0_exceptions.py`):
```python
def h():
    print("h: start")
    raise ValueError("bad value")
    print("h: end")          # never runs

def g():
    print("g: start")
    h()
    print("g: end")          # never runs

def f():
    try:
        g()
    except ValueError as err:
        print("f caught:", err)
    print("f: end")          # runs: f carried on after catching

f()
```
**Output:**
```
g: start
h: start
f caught: bad value
f: end
```
Notice: `h: end` and `g: end` never print. **After an error, the rest of the `try` block is skipped.** But once it's caught, the program **continues normally** after the `try` statement.

### 0.2 Three questions for any `try/except`
1. **Which line can fail?** (Put only that in the `try`.)
2. **Which error type will it raise?** (That's what you write after `except`.)
3. **What should happen then?** Recover (use a default), translate (raise a better error), or let it travel up?

### 0.3 `except` matches by type, *including parent types*
Exceptions are classes, and classes inherit (yesterday's Part 2!). So `except Parent` also catches every child:
```
BaseException
 └─ Exception
     ├─ ValueError
     ├─ KeyError, IndexError
     ├─ OSError
     │    └─ FileNotFoundError
     └─ YourOwnError (anything you define as class YourOwnError(Exception))
```
- `except OSError` catches `FileNotFoundError` too.
- `except Exception` catches **almost everything**, which is why it's dangerous: it hides bugs.
- Python tries the `except` blocks **top to bottom** and runs **the first that matches**, so put the **specific** ones first.

### 0.4 The block order, once and for all
```python
try:
    ...        # risky code
except SomeError:
    ...        # runs only if SomeError happened
else:
    ...        # runs only if NO error happened
finally:
    ...        # runs ALWAYS: error or not, even if there's a return
```

### 0.5 Three patterns you'll use 95% of the time
```python
# 1. Fall back to a default
def safe_int(text, default=None):
    try:
        return int(text)
    except (ValueError, TypeError):
        return default

# 2. Translate a low-level error into a meaningful one (keeping the cause)
try:
    return users[user_id]
except KeyError as exc:
    raise NotFound(f"user {user_id} not found") from exc

# 3. Always clean up
try:
    use(resource)
finally:
    resource.close()          # (the `with` statement does this for you)
```
A bare `raise` inside an `except` block **re-raises the same error** (useful for "log it, then let it continue upward").

### 0.6 Five questions people secretly have
1. *Does the code after the failing line run?* **No**, not inside that `try`. The rest of the `try` block is skipped.
2. *If I catch the error, does the program stop?* **No.** It continues after the whole `try` statement.
3. *Does `else` run if an error was caught?* **No**, only when there was no error.
4. *Does `finally` run if there's a `return` inside?* **Yes.** It runs just before returning.
5. *Why not just `except:` everywhere?* It swallows **every** error, including your own typos, and makes bugs invisible.

### Quiz: predict the output (answers at the bottom)
```python
# E2
def risky(x):
    try:
        return 10 / x
    except ZeroDivisionError:
        return "div by zero"
    finally:
        print("cleanup")
print(risky(2))
print(risky(0))

# E3
try:
    [1, 2, 3][5]
except KeyError:
    print("key")
except IndexError:
    print("index")

# E4
try:
    try:
        int("x")
    except ValueError:
        print("inner")
        raise
except ValueError:
    print("outer")

# E5
class AppError(Exception): pass
class NotFound(AppError): pass
try:
    raise NotFound("missing")
except AppError as e:
    print("caught", type(e).__name__, e)

# E6
try:
    open("nope.txt")
except OSError:
    print("OS")
```
**Check yourself:** redo `safe_int` and `load_config` from Day 3 (exercises 7 and 9) from memory. If they pass, Part 0 is done.

**Part 0 done when**
- [ ] You can explain the hot-potato picture in your own words
- [ ] You got at least 4 of 5 quiz answers right (re-read the matching section for the others)

---

# Part 1 · Functions as values, closures, decorators (45 min)

### 1.1 Functions are objects
In Python a function is a value, just like a number or a string. You can store it in a variable, pass it to another function, and return it from one.
```python
def shout(text: str) -> str:
    return text.upper()

f = shout                 # no parentheses: f now refers to the SAME function
print(f("hi"))            # HI

def apply_twice(fn, value):
    return fn(fn(value))

print(apply_twice(shout, "a"))     # A

print(sorted(["bb", "a", "ccc"], key=len))    # you've already passed a function: `len`
```
`shout` (no parentheses) **is** the function. `shout("hi")` (with parentheses) **calls** it and gives the result.

### 1.2 Closures: an inner function that remembers
A function can be defined **inside** another, and it **remembers the variables** of the outer function even after the outer one has finished:
```python
def make_counter():
    count = 0
    def inc():
        nonlocal count          # "I mean the outer count, not a new local one"
        count += 1
        return count
    return inc                  # return the inner function itself

c1 = make_counter()
c2 = make_counter()
print(c1(), c1(), c2())         # 1 2 1   ← each counter remembers its OWN count
```
That's a **closure**. It's the building block of decorators.

### 1.3 What a decorator is
> A **decorator** is a function that **takes a function and returns a (new) function**, usually one that wraps the original with extra behaviour.

The `@` line is just a **shortcut**:
```python
@timed
def slow_add(a, b): ...

# means exactly:
def slow_add(a, b): ...
slow_add = timed(slow_add)
```
Here's the whole thing, with comments on each step:
```python
import time
from functools import wraps


def timed(func):                          # (1) receives the original function
    @wraps(func)                          # (4) copies the original's name/docstring onto the wrapper
    def wrapper(*args, **kwargs):         # (2) the NEW function that replaces the original
        start = time.perf_counter()
        result = func(*args, **kwargs)    #     calls the ORIGINAL with whatever arguments it was given
        elapsed = (time.perf_counter() - start) * 1000
        print(f"{func.__name__} took {elapsed:.2f} ms")
        return result                     #     hands back the original's result
    return wrapper                        # (3) returns the new function


@timed
def slow_add(a: int, b: int) -> int:
    time.sleep(0.2)
    return a + b


print(slow_add(1, 2))
```
**What happens, step by step:**
1. Python defines `slow_add`, then runs `slow_add = timed(slow_add)`.
2. `timed` builds `wrapper` and returns it. **The name `slow_add` now points at `wrapper`.**
3. When you call `slow_add(1, 2)`, you're really calling `wrapper(1, 2)`. It starts a timer, calls the **original** `slow_add`, prints the time, and returns the result.

Why `*args, **kwargs`? So the wrapper accepts **whatever arguments** the original takes and passes them straight through (Day 1's `*args`/`**kwargs`, finally useful).

Why `@wraps(func)`? Without it, `slow_add.__name__` would say `"wrapper"` and the docstring would be lost, which confuses debugging tools and (importantly) frameworks like FastAPI that read function names and signatures.

**A decorator runs at definition time.** The moment Python reaches `@timed def …`, it calls `timed`. The *wrapper* runs later, on each call.

### 1.4 Decorators with arguments: three layers
`@repeat(3)` has parentheses, so `repeat(3)` is **called first** and must return the actual decorator:
```python
def repeat(times: int):                       # layer 1: receives the decorator's arguments
    def decorator(func):                      # layer 2: receives the function
        @wraps(func)
        def wrapper(*args, **kwargs):         # layer 3: runs on each call
            return [func(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator

@repeat(3)
def hi():
    return "hi"

print(hi())     # ['hi', 'hi', 'hi']
```
`@repeat(3)` means `hi = repeat(3)(hi)`. Read it as: "call `repeat(3)` to get a decorator, then apply that decorator to `hi`."

### 1.5 This is how `@app.get("/users")` works
A decorator doesn't have to wrap the function at all. It can just **register** it in a table and hand it back unchanged:
```python
ROUTES = {}

def route(path: str):
    def decorator(func):
        ROUTES[path] = func          # remember: this path is handled by this function
        return func                  # give the original back untouched
    return decorator

@route("/hello")
def hello():
    return "hi"

print(ROUTES)          # {'/hello': <function hello at 0x...>}
ROUTES["/hello"]()     # 'hi': the "framework" looks up the path and calls your function
```
That is **exactly** the idea behind `@app.get("/users")`: it stores *"GET /users is handled by this function"*. FastAPI then adds the clever parts: reading the request, validating data, turning your return value into JSON.

You've already used other decorators: `@property`, `@classmethod`, `@dataclass`. And `@pytest.fixture` is coming up in Part 3.

### 1.6 Common mistakes
- Forgetting `return wrapper` (the decorated name becomes `None`).
- Forgetting to `return` the **original's result** inside `wrapper` (the decorated function now returns `None`).
- Forgetting `@wraps(func)`.
- Writing `@repeat` when you need `@repeat(3)` (and vice versa).
- Calling the function inside the decorator (`func()`), instead of returning the wrapper.

### Type it → `drills/d4_p1_decorators.py`
Type `timed`, `repeat` and `route` from above. Run them. Then print `slow_add.__name__`, and remove `@wraps(func)` to see the difference.

### Predict the output (guess first; answers at the bottom)
```python
# D1
def make_counter():
    count = 0
    def inc():
        nonlocal count
        count += 1
        return count
    return inc
c1 = make_counter(); c2 = make_counter()
print(c1(), c1(), c2())

# D2: a decorator WITHOUT @wraps
def timed(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
@timed
def foo():
    """docstring"""
print(foo.__name__, foo.__doc__)

# D3: when does the decorator itself run?
def deco_a(f):
    print("decorating", f.__name__)
    return f
@deco_a
def bar():
    pass
print("after definition")
```

### Exercises: Part 1
1. **`shout`**: a decorator that makes a function's returned string UPPERCASE. It must keep the original's `__name__` and `__doc__`.
2. **`repeat(times: int)`**: a decorator factory. The decorated function returns a **list** of `times` results.
3. **`route(path: str, method: str = "GET")`**: registers the function in a dict called `ROUTES` under the key **`(method, path)`**, and returns the original function.
4. **`retry(times: int = 3)`**: calls the function up to `times` times and returns the first success; if **every** attempt fails, it re-raises the **last** error.

**Self-check**
```python
@shout
def greet(name):
    """say hi"""
    return f"hello {name}"

assert greet("asha") == "HELLO ASHA"
assert greet.__name__ == "greet" and greet.__doc__ == "say hi"

@repeat(3)
def hi():
    return "hi"

assert hi() == ["hi", "hi", "hi"]

@route("/hello")
def hello():
    return "hi"

@route("/items", method="POST")
def create_item():
    return "created"

assert ROUTES[("GET", "/hello")]() == "hi"
assert ROUTES[("POST", "/items")]() == "created"
assert hello() == "hi"

calls = {"n": 0}

@retry(times=3)
def flaky():
    calls["n"] += 1
    if calls["n"] < 3:
        raise RuntimeError("boom")
    return "ok"

assert flaky() == "ok" and calls["n"] == 3

fails = {"n": 0}

@retry(times=2)
def always_fails():
    fails["n"] += 1
    raise ValueError("nope")

assert raises(ValueError, always_fails)
assert fails["n"] == 2
print("D4 P1 OK")
```

**Part 1 done when**
- [ ] `D4 P1 OK` prints
- [ ] You can explain `@timed def f` = `f = timed(f)` in your own words
- [ ] You can say how `@app.get("/users")` works (it *registers* your function)

---

# Part 2 · Iterators, generators, context managers (40 min)

### 2.1 How a `for` loop really works
```python
nums = [10, 20]
it = iter(nums)      # get an "iterator" from the list
next(it)             # 10
next(it)             # 20
next(it)             # raises StopIteration: "no more items"
```
A `for` loop does exactly this: it calls `iter()`, calls `next()` again and again, and stops when `StopIteration` appears. Anything you can loop over is an **iterable**.

### 2.2 Generators: functions that can pause
A function with **`yield`** is a **generator function**. Calling it does **not** run the body. It gives you a **generator**; each `next()` runs the body **until the next `yield`**, hands out that value, and **pauses right there**, remembering everything.
```python
def count_up(limit):
    n = 1
    while n <= limit:
        print(f"  yielding {n}")
        yield n               # hand out n, then PAUSE here
        n += 1                # ...resumes here on the next next()

g = count_up(2)
print("created")              # nothing from the function body has run yet
print(next(g))                # runs until the first yield
print(next(g))                # resumes after the yield, runs to the next one
print(next(g, "done"))        # no more: next() returns the default "done"
```
**Output:**
```
created
  yielding 1
1
  yielding 2
2
done
```
Why use them? They're **lazy**: values are made **one at a time, on demand**, so a generator can produce a huge or even endless sequence using almost no memory.

A **generator expression** is a lazy list comprehension with round brackets: `(n * n for n in range(4))`. **A generator is one-shot**: once you've looped over it, it's empty (`list(gen)` a second time gives `[]`).

### 2.3 Context managers: `with` = guaranteed cleanup
```python
with open("notes.txt", encoding="utf-8") as f:
    text = f.read()
# the file is closed here, even if an error occurred inside the block
```
A **context manager** does something when you **enter** the `with` block (open, connect, start) and something when you **leave** it (close, disconnect), **even if an error happened**.

The easiest way to write one is a **generator with exactly one `yield`**:
```python
from contextlib import contextmanager

@contextmanager
def opened(name: str):
    print(f"open {name}")             # runs on ENTER
    try:
        yield name                    # the `with` block runs here; `as x` receives `name`
    finally:
        print(f"close {name}")        # runs on LEAVE: always, even after an error

with opened("db") as db:
    print("using", db)
# open db / using db / close db
```
Shape to remember: **setup → `try:` → `yield` → `finally:` → cleanup.**

### 2.4 This is FastAPI's `get_db`
Remember the database session in your future code:
```python
def get_db():
    db = SessionLocal()       # setup: open a session
    try:
        yield db              # PAUSE: your endpoint runs now, using `db`
    finally:
        db.close()            # cleanup: runs after the request, even if it crashed
```
FastAPI drives it like this: it calls `next()` once (runs until `yield`, hands your endpoint the `db`), runs your endpoint, then calls `next()` again (resumes after the `yield`, so the `finally` closes the session). And if your endpoint raises an error, FastAPI throws it into the generator at the `yield`, so the `finally` **still runs**. You'll simulate exactly this in exercise 8 below.

### 2.5 Common mistakes
- Treating a generator like a list (indexing it, or looping twice).
- Forgetting the `try/finally` around the `yield` in a context manager (then cleanup is skipped after an error).
- Writing `return value` where you meant `yield value`.

### Type it → `drills/d4_p2_generators.py`
Type `count_up`, the generator expression, and `opened` exactly as above. Run them and compare the output with the text.

### Predict the output (guess first; answers at the bottom)
```python
# G1
squares = (n * n for n in range(4))
print(list(squares), list(squares))
```
(And re-read the `count_up` output above: could you have predicted the order of the lines? Try again without looking.)

### Exercises: Part 2
(imports at the top: `from collections.abc import Iterator`, `from contextlib import contextmanager`, `from itertools import islice`)
5. **`fibonacci() -> Iterator[int]`**: an **endless** generator: `0, 1, 1, 2, 3, 5, …`
6. **`chunks(items: list, size: int) -> Iterator[list]`**: yields consecutive slices of length `size` (the last may be shorter).
7. **`collect(log: list[str], name: str)`**: a `@contextmanager` that appends `"open <name>"` on entering and `"close <name>"` in a `finally`.
8. **`FakeSession`** (a class with `closed = False` and a `close()` method that sets `self.closed = True`) and **`get_session()`**: a generator that creates a session, yields it, and closes it in a `finally`.

**Self-check**
```python
assert list(islice(fibonacci(), 8)) == [0, 1, 1, 2, 3, 5, 8, 13]
assert list(chunks([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
assert list(chunks([], 3)) == []

log: list[str] = []
with collect(log, "db"):
    log.append("working")
assert log == ["open db", "working", "close db"]

def use_and_fail(entries: list[str]) -> None:
    with collect(entries, "db"):
        raise ValueError("boom")

log.clear()
assert raises(ValueError, use_and_fail, log)
assert log == ["open db", "close db"]       # cleanup ran even though it crashed

gen = get_session()                  # this is how FastAPI drives a dependency:
session = next(gen)                  # 1) run until the yield → the endpoint gets the session
assert session.closed is False
assert next(gen, None) is None       # 2) request finished → resume → the finally runs
assert session.closed is True

gen = get_session()
session = next(gen)
assert raises(ValueError, gen.throw, ValueError("boom"))   # the endpoint crashed
assert session.closed is True                              # ...and the session still got closed
print("D4 P2 OK")
```
(`islice(gen, 8)` takes the first 8 items from an endless generator.)

**Part 2 done when**
- [ ] `D4 P2 OK` prints
- [ ] You can explain what `yield` does (pauses; resumes on the next `next()`)
- [ ] You can explain what runs before and after the `yield` in `get_db`, and when

---

# Part 3 · pytest, debugging, logging (45 min)

### 3.1 Setup (5 min)
From the `python-fundamentals` folder:
```bash
uv add --dev pytest ruff
```
Open `pyproject.toml` (in VS Code) and add these lines at the very **bottom**:
```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```
That tells pytest to look for tests in the `tests/` folder and to treat the project root as importable.

### 3.2 pytest in five ideas
1. Test files are named **`test_*.py`**; test functions are named **`test_*`**.
2. A test is just a function with a plain **`assert`**. If an assert is false, the test **fails**.
3. **`pytest.raises(SomeError)`** checks that code raises an error.
4. A **fixture** (`@pytest.fixture`) builds something tests need; any test that lists it as a parameter receives it. The built-in **`tmp_path`** fixture gives each test a fresh temporary folder.
5. **`@pytest.mark.parametrize`** runs the same test for many inputs.

Run: `uv run pytest -v`. When a test fails, pytest shows you the line and **what it expected vs what it got**. Read that diff: it usually tells you the bug.

### 3.3 Build and test
Create `practice/__init__.py` (empty) and `practice/mathx.py`:
```python
def is_prime(n: int) -> bool:
    ...   # you write it: n < 0 raises ValueError; 0 and 1 are not prime
```
Then **type** `tests/test_practice.py`:
```python
import pytest

from practice.mathx import is_prime


@pytest.mark.parametrize("n, expected", [
    (0, False), (1, False), (2, True), (3, True), (4, False), (17, True), (21, False), (97, True),
])
def test_is_prime(n, expected):
    assert is_prime(n) is expected


def test_is_prime_rejects_negative_numbers():
    with pytest.raises(ValueError):
        is_prime(-1)


@pytest.fixture
def notes_file(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("line one\nline two\n", encoding="utf-8")
    return path


def test_fixture_gives_a_real_file(notes_file):
    assert notes_file.read_text(encoding="utf-8").splitlines() == ["line one", "line two"]
```
Run `uv run pytest -v`. **Expect:** 10 tests, all passing (the 8 parametrized cases count as 8).
- **Red → green:** first run it with `is_prime` still `...` and watch the tests **fail**. Then write `is_prime` until they pass. (*Hint: a number is prime if no integer from 2 up to its square root divides it.*)
- **Break it on purpose:** change one expected value in a test, run it, and **read the failure output** (it shows `assert False is True` and which case).

### 3.4 Debugging: find bugs instead of guessing
Order of attack:
1. **Read the error from the bottom up** (Part 0 and yesterday's traceback section).
2. **Use the debugger**, so you can *watch* the program instead of imagining it.

**VS Code debugger on a Mac:**
1. Click in the **gutter** (the space just left of a line number). A **red dot** appears: a *breakpoint*. The program will **pause there**.
2. Open the **Run and Debug** panel (the play-with-a-bug icon in the left bar, or `Shift+Cmd+D`) → click **Run and Debug** → choose **Python File**.
3. The program stops at your red dot. Use the **toolbar at the top** (click the buttons; on a Mac laptop the function keys may need `fn` held): **Continue**, **Step Over** (run this line), **Step Into** (go inside a function call), **Step Out**, **Restart**, **Stop**.
4. Watch the **Variables** panel on the left: values change as you step.
5. The **Debug Console** at the bottom lets you type an expression to check a value.

**Exercise: find the planted bug.** Type exactly this into `drills/d4_p3_debug.py`:
```python
def average(numbers):
    total = 0
    for i in range(1, len(numbers)):
        total += numbers[i]
    return total / len(numbers)

print(average([10, 20, 30]))      # should print 20.0
```
It prints `16.666…`. **Don't read the code for the answer.** Put a breakpoint on `total += numbers[i]`, start the debugger, step through, and **watch `i` and `total`**. When you see it, fix it.
Then move `average` into `practice/mathx.py` (and make an **empty list raise `ValueError`**), and add two tests to `tests/test_practice.py`:
- `average([10, 20, 30]) == 20`
- `average([])` raises `ValueError`
(`print(f"{variable=}")` is a fine quick alternative to the debugger.)

### 3.5 Logging: `print` with superpowers
`print` has no levels, no timestamps, and no off switch. Real programs **log**. Type this into `drills/d4_p3_logging.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

logger.debug("debug: very detailed")
logger.info("info: normal event")
logger.warning("warning: something odd")
logger.error("error: something failed")

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("failed to divide")      # logs the message AND the full traceback
```
Run it. **Expect:** INFO, WARNING and ERROR lines with timestamps, then the traceback; **DEBUG does not appear** (the level is INFO). Change `logging.INFO` to `logging.DEBUG` and run again: now it appears. In production you keep INFO and switch to DEBUG only when hunting a problem.

The five levels, from quietest to loudest: `DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`.

### 3.6 Ruff: tidy code automatically (3 min)
```bash
uv run ruff format .
uv run ruff check .
```
`format` fixes the layout; `check` finds mistakes (unused imports, etc.). Fix what it reports (`uv run ruff check --fix .` handles many).

**Part 3 done when**
- [ ] `uv run pytest -v` shows **12 passed** (10 + your 2 `average` tests)
- [ ] You found the `average` bug using the debugger, not by staring
- [ ] The logging output matches the description (no DEBUG at INFO level)
- [ ] `ruff check .` reports no problems

---

# Part 4 · async: see it once (15 min)

### 4.1 The idea
Normal code **waits**: when it asks a database or another server for something, the program just sits there until the answer comes back. An **`async def`** function can **pause at an `await`** and let *other work* run while it waits. It all happens on **one thread**; it's about not wasting the waiting time.

- It helps when you're **waiting** (network, database, disk).
- It does **not** speed up heavy **computation**.
- `await` can only be used inside an `async def`.
- Calling an `async def` function **doesn't run it**; you get a *coroutine object*. You must `await` it (or hand it to `asyncio.run`).
- **In FastAPI, for now, you'll write plain `def`.** FastAPI handles the rest. You'll learn the exact rule for `async def` on Day 21 of the plan.

### 4.2 Type it → `drills/d4_p4_async.py`
```python
import asyncio
import time


async def fetch(name: str, seconds: float) -> str:
    await asyncio.sleep(seconds)           # pretend: waiting for a database
    return f"{name} done"


async def sequential() -> list[str]:
    return [await fetch("a", 1), await fetch("b", 1), await fetch("c", 1)]


async def concurrent() -> list[str]:
    return await asyncio.gather(fetch("a", 1), fetch("b", 1), fetch("c", 1))


for fn in (sequential, concurrent):
    start = time.perf_counter()
    result = asyncio.run(fn())
    print(fn.__name__, result, f"{time.perf_counter() - start:.1f}s")
```
**Predict first**, then run. **Expect:** `sequential` takes about **3.0 s** (one after another), `concurrent` about **1.0 s** (all three waits overlap).

**Break it:** add a line `print(fetch("a", 1))` (no `await`). You'll see `<coroutine object fetch at 0x…>` and a warning `coroutine 'fetch' was never awaited`. That is **the #1 async mistake**.

**Part 4 done when**
- [ ] You saw ≈ 3 s vs ≈ 1 s
- [ ] You can say in one sentence when async helps

---

## Wrap-up (10 min)

**1. Explain without notes** (aloud, or 1–2 lines each)
1. What is a decorator, in one sentence? What does `@wraps` do?
2. How does `@app.get("/users")` work under the hood?
3. Generator vs list: when does a generator win?
4. In `get_db`, what runs before `yield`, what runs after, and when?
5. What's a fixture? What does `parametrize` save you?
6. Why `logging` instead of `print`?
7. When does `async` help, and when doesn't it?

**2. Cheat sheet:** one line per question in `notes/00-python-cheatsheet.md`, in your own words with the smallest example.

**3. Journal** (`journal.md`): `Did: … / Confused me: … / Tomorrow starts with: …`

**4. Commit and push** (VS Code Source Control: message, **Commit**, **Sync/Push**), or:
```bash
cd ~/backend-journey
git add .
git commit -m "day 4: decorators, generators, tests, async"
git push
```

**Tomorrow (Day 5):** the tools day. Install **Docker Desktop for Mac** and **Bruno**, run **PostgreSQL** in Docker, your first **FastAPI hello-world**, plus the **Log Analyzer** project that proves your Python. Tell me **"Day 5 please"** and anything that confused you today. *(Tip: Docker Desktop is a big download. You can start it tonight, and it'll be ready in the morning.)*

### Day 4 done when
- [ ] `D4 P1 OK`, `D4 P2 OK`, 12 tests passing, `ruff check .` clean, async ≈ 3 s vs ≈ 1 s
- [ ] The exception quiz is answered
- [ ] Cheat sheet lines, journal, and commit done

*(If Part 3 and Part 4 slip to the buffer day, that's fine. Mark them `TODO` in your journal.)*

---

# Quick reference (keep this)

```python
# decorator
def deco(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ...                       # before
        result = func(*args, **kwargs)
        ...                       # after
        return result
    return wrapper

# decorator with arguments: three layers
def deco_with(arg):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# generator + context manager shape
def get_db():
    db = open_something()      # setup
    try:
        yield db               # pause: the caller uses db
    finally:
        db.close()             # cleanup, even after an error
```
**Rules:** `@x def f` = `f = x(f)` · decorators run at definition time · `@wraps` keeps the name · a generator pauses at `yield` and is one-shot · `with` = guaranteed cleanup · tests: `test_*` functions with `assert`, `pytest.raises`, fixtures, `parametrize` · debug with breakpoints, not guessing · log with levels, not print · `await` only inside `async def`; `async` helps when waiting, not computing.

**Mac keys/commands:** `uv run pytest -v` · `uv run ruff format .` · `uv run ruff check .` · `Shift+Cmd+D` (Run and Debug) · `Cmd+T` (new Terminal tab)

---

# Solutions (open only after 20 minutes of trying one exercise)

Read one, close the file, **retype it from memory**.

### Part 1
```python
from functools import wraps


def shout(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper


def repeat(times: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator


ROUTES = {}


def route(path: str, method: str = "GET"):
    def decorator(func):
        ROUTES[(method, path)] = func
        return func
    return decorator


def retry(times: int = 3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for _ in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_error = exc
            raise last_error
        return wrapper
    return decorator
```

### Part 2
```python
from collections.abc import Iterator
from contextlib import contextmanager


def fibonacci() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def chunks(items: list, size: int) -> Iterator[list]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


@contextmanager
def collect(log: list[str], name: str):
    log.append(f"open {name}")
    try:
        yield
    finally:
        log.append(f"close {name}")


class FakeSession:
    closed = False

    def close(self) -> None:
        self.closed = True


def get_session():
    session = FakeSession()
    try:
        yield session
    finally:
        session.close()
```

### Part 3
```python
# practice/mathx.py
def is_prime(n: int) -> bool:
    if n < 0:
        raise ValueError("n must be >= 0")
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True


def average(numbers):
    if not numbers:
        raise ValueError("average of empty list")
    total = 0
    for i in range(len(numbers)):     # the bug was range(1, ...): it skipped index 0
        total += numbers[i]
    return total / len(numbers)
```
Tests to add:
```python
from practice.mathx import average, is_prime

def test_average():
    assert average([10, 20, 30]) == 20

def test_average_of_empty_list_raises():
    with pytest.raises(ValueError):
        average([])
```

---

# Answers: predict the output

**Part 0 (exceptions)**
- **E2:** prints `cleanup`, `5.0`, `cleanup`, `div by zero` (`finally` runs both times, even with the `return`).
- **E3:** `index` (the error is an `IndexError`, and Python takes the first `except` that matches).
- **E4:** `inner` then `outer` (a bare `raise` re-raises the same error to the outer handler).
- **E5:** `caught NotFound missing` (`NotFound` is a child of `AppError`, so `except AppError` catches it).
- **E6:** `OS` (`FileNotFoundError` is a subclass of `OSError`).

**Part 1 (decorators)**
- **D1:** `1 2 1`. Each counter remembers its own `count`.
- **D2:** `wrapper None`. Without `@wraps` the name and docstring are lost.
- **D3:** `decorating bar` then `after definition`. The decorator runs when the function is defined, not when it's called.

**Part 2 (generators)**
- **G1:** `[0, 1, 4, 9] []`. A generator is one-shot: the second `list()` finds it empty.

# Python Day 1 Cheatsheet

Quick refresher for **functions, data structures, files, JSON, paths, and enums**.

## References

- [Block 1: functions](../drills/d1_b1_functions.py)
- [Block 2: data structures](../drills/d1_b2_data.py)
- [Block 2: exercises/questions](../drills/d1_b2_data_question.py)
- [Block 3: files, JSON, paths, and enums](../drills/d1_b3_files.py)
- [Block 3: exercises/questions](../drills/d1_b3_files_question.py)

## 1. Functions

- Prefer returning values over printing them: returned values can be reused and tested.
- Type hints document expected shapes and are used by tools/frameworks such as Pydantic and FastAPI:
  `list[str]`, `dict[str, int]`, `str | None`, `int | float`, `tuple[int, str]`.
- Defaults and keyword arguments:
  `greet("Asha", excited=True)`.
- Parameters after `*` are keyword-only:
  `def full_name(first, last, *, middle=None): ...`
- In a definition:
  - `*args` collects extra positional arguments into a **tuple**.
  - `**kwargs` collects extra keyword arguments into a **dict**.
- In a call:
  - `f(*items)` unpacks an iterable into positional arguments.
  - `f(**data)` unpacks a dict into keyword arguments.
- Never use `[]` or `{}` as a mutable default. Use `None`, then create a new list/dict inside:

  ```python
  def add_item(item: str, bucket: list[str] | None = None) -> list[str]:
      if bucket is None:
          bucket = []
      bucket.append(item)
      return bucket
  ```

  A default is created once when the function is defined, so a default list is shared across calls.

## 2. Collections and loops

```python
nums = [1, 2, 3, 4, 5, 6]
evens = [n for n in nums if n % 2 == 0]
squares = {n: n * n for n in nums}
lengths = {len(word) for word in ["a", "bb", "cc"]}
flat = [x for row in [[1, 2], [3]] for x in row]
```

- `dict.get("key", default)` avoids `KeyError`.

### Counting, grouping, and sorting

```python
from collections import Counter, defaultdict

# Counter: count repeated values
counts = Counter("mississippi")
counts.most_common(2)  # [("i", 4), ("s", 4)]

# defaultdict: create a default value for a missing key
groups = defaultdict(list)
groups[3].append("sup")
groups[3].append("hey")
# {3: ["sup", "hey"]}; the key is the int 3

# sorted(..., key=...): calculate the value used for comparison
people = [("zed", 30), ("amy", 25)]
sorted(people, key=lambda person: person[1])  # age, ascending
```

`lambda` is a small anonymous function. In `key=lambda person: person[1]`,
each item is passed to the lambda and sorted by the returned value.

For multiple rules, return a tuple. Negate numbers for descending order:

```python
scores = {"zed": 5, "amy": 9, "bob": 9, "cy": 1}
sorted(scores, key=lambda name: (-scores[name], name))
# ["amy", "bob", "zed", "cy"]: score descending, name ascending for ties
```

Tuples compare element by element, so `(-score, name)` means:
1. highest score first; 2. alphabetically first when scores tie.

- `enumerate(items, start=1)` gives `(index, value)`.
- `zip(a, b)` gives pairs and stops at the shortest iterable.
- `any(condition for item in items)` is true if at least one condition is true.
- `all(condition for item in items)` is true only if every condition is true.
- `any()` and `all()` short-circuit: `any()` stops at the first `True`; `all()` at the first `False`.
- Unpacking:
  `first, *rest = [1, 2, 3]`; `a, b = b, a`.

### Mutability and copying

```python
a = [1, 2]
b = a          # same list; changes through b affect a
c = a.copy()   # shallow copy; independent outer list
```

Avoid repeated-row aliases:

```python
bad = [[0] * 2] * 2
good = [[0] * 2 for _ in range(2)]
```

## 3. Strings and formatting

```python
f"{name!r}"       # repr, e.g. 'Asha'
f"{price:,.2f}"   # 1,234,567.89
f"{name:>8}"      # right-align in width 8
f"{number:03d}"   # zero-pad integer, e.g. 007
f"{price=}"       # debugging form: price=123.45
```

## 4. Paths and text files

Use `pathlib.Path` instead of manually joining path strings.

```python
from pathlib import Path

p = Path("scratch") / "notes" / "a.txt"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("hello", encoding="utf-8")
text = p.read_text(encoding="utf-8")
```

- `p.parent`: containing directory
- `p.exists()`: whether the path exists
- `p.name`: filename, such as `a.txt`
- `p.stem`: filename without extension, such as `a`
- `p.suffix`: extension, such as `.txt`
- `p.iterdir()`: children of a directory

Always specify `encoding="utf-8"` for text reads and writes.

## 5. JSON

JSON is text; a dict is a Python data structure.

| Python | JSON |
|---|---|
| `dict`, `list`, `str` | object, array, string |
| `True` / `False` | `true` / `false` |
| `None` | `null` |
| single or double quotes in source | double quotes |
| tuples become arrays | sets and arbitrary custom objects are unsupported by default |

```python
import json

text = json.dumps({"a": 1}, indent=2)  # Python value -> JSON string
data = json.loads(text)                # JSON string -> Python value
json.dump(data, file, indent=2)        # Python value -> open file
data = json.load(file)                 # open file -> Python value
```

## 6. `StrEnum`

Use a `StrEnum` for a fixed set of string choices:

```python
from enum import StrEnum

class Status(StrEnum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"

Status("done")       # Status.DONE; invalid value raises ValueError
Status.DONE.value    # "done"
Status.DONE == "done"  # True
```

Because members behave like strings, they work naturally with JSON and FastAPI.

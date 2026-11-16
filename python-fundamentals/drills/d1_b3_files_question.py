from pathlib import Path
import json
from enum import StrEnum
from collections import defaultdict, Counter
from d1_b1_functions import raises


def format_money(amount: float, currency: str = "INR") -> str:
    return f"{currency} {amount:,.2f}"


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


class Status(StrEnum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


def count_files_by_extension(folder: Path) -> dict[str, int]:
    return Counter([child.suffix for child in folder.iterdir()])


# claude tests
assert format_money(1234567.891) == "INR 1,234,567.89"
assert format_money(5, "USD") == "USD 5.00"

p = Path("scratch") / "a" / "data.json"
save_json({"name": "Asha", "tags": ["x", "y"]}, p)
assert p.exists()
assert load_json(p) == {"name": "Asha", "tags": ["x", "y"]}
assert load_json(Path("scratch/missing.json"), default={}) == {}
assert '  "name"' in p.read_text(encoding="utf-8")

assert Status("done") is Status.DONE
assert Status.DONE == "done"
assert json.dumps({"s": Status.DONE}) == '{"s": "done"}'
assert [s.value for s in Status] == ["todo", "doing", "done"]
assert raises(ValueError, Status, "nope")

folder = Path("scratch/files")
folder.mkdir(parents=True, exist_ok=True)
for fname in ("a.py", "b.py", "c.txt", "README"):
    (folder / fname).write_text("x", encoding="utf-8")
assert count_files_by_extension(folder) == {".py": 2, ".txt": 1, "": 1}
print("D1 B3 OK")

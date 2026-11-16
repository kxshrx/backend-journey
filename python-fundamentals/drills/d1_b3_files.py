# f-strings and format specs
name, price = "Asha", 1234567.891
f"{name!r}"
f"{price:,.2f}"
f"{name:<8}|{3:03d}"
f"{price=}"

# f"{3:03d}"   # "003"
# f"{7:03d}"   # "007"
# f"{25:03d}"  # "025"

# pathlib: paths as objects (never glue strings with "/")
from pathlib import Path

p = Path("scratch") / "notes" / "a.txt"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("hello this is me", encoding="utf-8")  
p.read_text(encoding="utf-8")
p.exists()
p.name
p.suffix
p.stem
for child in p.parent.iterdir():
    ...


import json

text = json.dumps({"a": 1}, indent=2)
data = json.loads(text)


# StrEnum: a fixed set of named choices that are also strings
from enum import StrEnum


class Status(StrEnum):
    TODO = "todo"
    DONE = "done"


Status("done")  # Status.DONE  (lookup by value; bad value -> ValueError)
Status.DONE.value  # "done"
Status.DONE == "done"

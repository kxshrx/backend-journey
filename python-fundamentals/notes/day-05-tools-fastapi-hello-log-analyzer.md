# Day 5: Tools day: your first server, Docker, PostgreSQL, Bruno, Log Analyzer

> Module 1, Day 5 of 30 · about 3.5 hours including breaks and installs · written for a **Mac**
> **Everything you need for today is in this file.** Don't look anything else up.
> Save it as `notes/days/day-05.md` in your `backend-journey` repo.

---

## Read this first

Yesterday was plumbing. **Today you build things you can see and touch**:
1. **Your own web server**, running on your Mac, that you talk to from the browser and Terminal. (The "server" you played by hand with `nc` on Day 2: now it's real.)
2. A **database** running in Docker.
3. A tool to poke your server with requests (**Bruno**).
4. A small **Python project** that reads a log file and produces a report.

And here is the payoff for the "boring" Day 3 and 4 topics: in Part 1 you'll see **`@app.get`** (a decorator), **`class Item(BaseModel)`** (inheritance) and **type hints** all doing real work. They'll finally have a reason to exist.

**Order is on purpose:** the quick win (a working server) comes first, while energy is highest.

**Floor rule (zero-energy day):** Step 0 + Part 1 alone counts as a day.

---

## How today works

| Part | Time | What |
|---|---|---|
| Check-in | 5 min | **Recall** 3 things from yesterday without looking; "today I'm done when…" in `journal.md` |
| **Step 0** | 10 min | Start the downloads (Docker, Bruno) so they install while you work |
| **Part 1** | 40 min | Your first FastAPI server |
| **Part 2** | 15 min | Bruno: a friendly tool for sending requests |
| Break | 5 min | Walk, water |
| **Part 3** | 50 min | Docker + PostgreSQL |
| Break | 10 min | Eat something |
| **Part 4** | 60 min | Python project: Log Analyzer |
| Wrap-up | 10 min | Questions, cheat sheet, commit |

**Stuck?** 5 minutes → write `TODO` in your journal and move on · 20 minutes → ask an AI for a *hint* using the prompt in `01-fastapi-start-here.md`. **A solution for the Log Analyzer is at the bottom** (look only after 20 minutes of honest trying on one function, then close it and retype).

---

## Step 0 · Start the downloads (10 min)

1. **Docker Desktop for Mac.** Open docker.com → *Docker Desktop* → **Download for Mac**. You must pick the right chip: click the Apple menu → **About This Mac** and see whether it says **Apple (M1/M2/M3/M4…)** or **Intel**. It's a big file; let it download while you work on Part 1.
2. **Bruno.** Open usebruno.com → **Download** → pick the Mac version (Apple Silicon or Intel, same check as above).
3. Make the folders (from the repo root):
```bash
cd ~/backend-journey          # adjust if your repo is elsewhere
mkdir -p playground proofs infra
```
(Nothing happens if they already exist.)

---

# Part 1 · Your first FastAPI server (40 min)

### 1.1 What you're about to do
You'll write a Python file with a few functions. A program called **uvicorn** will **listen on port 8000** (Day 1: a port on `127.0.0.1`), read incoming **HTTP requests** (Day 2), call **your function** that matches the URL, and send back an **HTTP response**. **FastAPI** is the layer that makes that matching and checking easy.

### 1.2 Set up the project
```bash
cd ~/backend-journey/playground
uv init --python 3.12
uv add "fastapi[standard]"
```
`uv init` makes a project (`pyproject.toml` and a few files). `uv add` installs FastAPI (and uvicorn, and a `fastapi` command) into it.

### 1.3 Type this into `playground/hello.py`
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Hello API")


@app.get("/")
def hello():
    return {"message": "backend journey begins"}


@app.get("/greet/{name}")
def greet(name: str, excited: bool = False):
    text = f"Hello, {name}" + ("!" if excited else ".")
    return {"greeting": text}


@app.get("/add")
def add(a: int, b: int):
    return {"result": a + b}


class Item(BaseModel):
    name: str
    price: float


@app.post("/items", status_code=201)
def create_item(item: Item):
    return {"received": item.model_dump(), "price_with_tax": round(item.price * 1.18, 2)}
```
**Type it, don't paste.** Read each function once: they are ordinary Python functions.

### 1.4 Run it
```bash
uv run fastapi dev hello.py
```
**Expect** a few lines ending with something like `Uvicorn running on http://127.0.0.1:8000`. **Leave this terminal running** (it's your server).
- `fastapi dev` = the **development** server: it **auto-reloads** whenever you save the file.
- `127.0.0.1:8000` = this machine, port 8000 (Day 1).
- If you see `Address already in use`, something else uses port 8000: find it with `lsof -i :8000` and stop it.

### 1.5 Try it (open a **second Terminal tab** with `Cmd+T` for the `curl` commands)
In your **browser**, open each of these and write down what you see:
- [ ] `http://localhost:8000/` → `{"message": "backend journey begins"}`
- [ ] `http://localhost:8000/greet/Asha` → `Hello, Asha.`
- [ ] `http://localhost:8000/greet/Asha?excited=true` → `Hello, Asha!` (a **query parameter**: Day 2)
- [ ] `http://localhost:8000/add?a=2&b=3` → `{"result": 5}`
- [ ] `http://localhost:8000/add?a=2&b=x` → an **error** with status **422**. **Read the message**: FastAPI tells you which field (`b`), where (`query`), and why ("not a valid integer"). **You wrote no validation code.** FastAPI got it from your type hint `b: int`.
- [ ] `http://localhost:8000/docs` → an **interactive page** listing your endpoints. Click one → **Try it out** → **Execute**. FastAPI built this page automatically from your code.
- [ ] `http://localhost:8000/openapi.json` → the machine-readable description of your API that `/docs` is drawn from.

### 1.6 See it as raw HTTP (Day 2, now with *your* server)
In the second tab:
```bash
curl -i "http://localhost:8000/add?a=2&b=3"
```
**Expect:** `HTTP/1.1 200 OK`, headers including `server: uvicorn` and `content-type: application/json`, a blank line, then `{"result":5}`. That's the 4-part response from Day 2, made by your code.
```bash
curl -i -X POST http://localhost:8000/items \
     -H "Content-Type: application/json" \
     -d '{"name":"pen","price":10}'
```
**Expect:** `HTTP/1.1 201 Created` and a JSON body with `"price_with_tax": 11.8`.
```bash
curl -i -X POST http://localhost:8000/items \
     -H "Content-Type: application/json" \
     -d '{"name":"pen","price":"abc"}'
```
**Expect:** `422` and a message that `price` isn't a valid number.

**Watch the first terminal** (where the server runs). Every request you made is logged, like `"GET /add?a=2&b=3 HTTP/1.1" 200 OK`. That's the request line from Day 2.

### 1.7 Break it on purpose (and match each to a status code from Day 2)
- [ ] `curl -i "http://localhost:8000/add?a=2"` → **422**, "Field required" for `b`
- [ ] `curl -i -X POST "http://localhost:8000/add?a=2&b=3"` → **405 Method Not Allowed** (that URL only supports GET; look at the `allow:` header)
- [ ] `curl -i http://localhost:8000/nope` → **404 Not Found**
- [ ] Edit the message in `hello()`, **save**, and refresh the page: the change is live (auto-reload)

### 1.8 What just happened: the pieces that finally matter
| In your code | What it did | Where you learned it |
|---|---|---|
| `@app.get("/add")` | **Registered** your function for `GET /add` | Day 4: decorators (the `route` exercise!) |
| `a: int, b: int` | FastAPI converts the **query parameters** and **validates** them | Day 1: type hints |
| `name: str` in `/greet/{name}` | the **path parameter** | Day 2: path vs query |
| `class Item(BaseModel)` | `Item` *is a* BaseModel with extra fields: it gets validation and `.model_dump()` for free | Day 3: inheritance |
| `return {...}` | FastAPI turns it into **JSON** with the right `Content-Type` | Day 2: headers |
| `status_code=201` | the **status code** | Day 2: status codes |
| uvicorn listening on 8000 | the server | Day 1: ports |

Press `Ctrl+C` in the server tab to stop it when you're done (or keep it running for Part 2).

### Part 1 done when
- [ ] All the checkboxes in 1.5 and 1.7 are ticked
- [ ] You can explain, in two sentences, what happens between a browser asking for `/add?a=2&b=3` and the answer coming back

---

# Part 2 · Bruno: a friendly tool for requests (15 min)

`curl` is great but clumsy for JSON bodies and cookies. **Bruno** is an app for sending requests and saving them. You'll use it all through the plan (especially for login flows).

1. Install Bruno (drag it to Applications) and open it.
2. **Create a collection:** *Collections → Create Collection*: name **`taskforge`**, location: a new folder **`backend-journey/bruno`**. (Bruno stores requests as plain files, so they can go into Git.)
3. Make sure your server is running (Part 1.4).
4. **New Request** in the collection:
   - Name `hello`, method **GET**, URL `http://localhost:8000/` → **Send** (the arrow). The right-hand pane shows the **status**, **time**, **size**, **headers** and **body**.
5. Make a second request `create item`, method **POST**, URL `http://localhost:8000/items`. Open the **Body** tab → choose **JSON** → type `{"name": "pen", "price": 10}` → Send. **Expect `201`.** Change `10` to `"abc"` → Send → **`422`**.
6. **Use a variable instead of repeating the address:** top right, **environment** dropdown → **Configure** → create an environment `local` → add a variable `baseUrl` = `http://localhost:8000` → select that environment. Now write your URLs as `{{baseUrl}}/` and `{{baseUrl}}/add?a=2&b=3`.
7. Save the requests (`Cmd+S`).

*(If a button has a different name in your Bruno version, look for the nearest equivalent. The ideas are the same.)*

**Part 2 done when**
- [ ] You sent a GET and a POST from Bruno and saw both status codes
- [ ] You used `{{baseUrl}}` in at least one request

---

# Part 3 · Docker + PostgreSQL (50 min)

### 3.1 Docker in five lines
- Normally to use PostgreSQL you'd install it on your Mac, with all the mess that brings.
- With **Docker** you run it in a **container**: a lightweight, **isolated mini-computer** that runs one program with its own files. Delete it and your Mac is untouched.
- An **image** is the frozen template (`postgres:17`). A **container** is a running copy of an image.
- A **volume** is storage that lives *outside* the container, so data survives when the container is removed.
- **Docker Desktop** runs a small hidden Linux machine on your Mac to host the containers. That's why you have to install and open the app.

### 3.2 Install and check it works
1. Open the downloaded `.dmg`, drag **Docker** to Applications, open it, accept the terms. (You can skip signing in.) Wait until the whale icon in the menu bar stops animating and the app says it's running.
2. In Terminal:
```bash
docker --version
docker run hello-world
```
**Expect:** a version number, then a message starting `Hello from Docker!`. That means Docker downloaded an image and ran a container.
*If you see "Cannot connect to the Docker daemon": Docker Desktop isn't running yet. Open it and wait.*

### 3.3 The compose file
**Docker Compose** lets you describe your containers in a file. Create `infra/docker-compose.yml`:
```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: taskforge
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
volumes:
  pgdata:
```
Line by line:
- `services: db:` one container, named `db`.
- `image: postgres:17` which template to run (Docker downloads it the first time).
- `environment:` settings passed to Postgres: a user `dev`, password `dev`, and a first database called `taskforge`. (`dev`/`dev` is only OK because this database lives on your laptop. Never use it on a server.)
- `ports: ["5432:5432"]`: **host port : container port.** "Connections to port 5432 on *my Mac* go to port 5432 *inside the container*." (Day 1: this is how your programs reach it.)
- `volumes: pgdata:/var/lib/postgresql/data`: store the database files in a **named volume** `pgdata`, so your data survives restarts.

### 3.4 Start it
```bash
cd ~/backend-journey/infra
docker compose up -d
docker compose ps
docker compose logs db | tail -5
```
- `up -d` starts it in the background (`-d` = detached). The first time it downloads the image; wait.
- **Expect** `docker compose ps` to show `db` as running (or "Up"), and the last log lines to include **`database system is ready to accept connections`**.

### 3.5 Talk to PostgreSQL
```bash
docker compose exec db psql -U dev -d taskforge -c "select version();"
docker compose exec db createdb -U dev taskforge_test
docker compose exec db psql -U dev -l
```
- `exec db …` runs a command **inside** the container. `psql` is Postgres's command-line client.
- **Expect:** a line with `PostgreSQL 17…`; then (no output) for `createdb`; then a list of databases that includes `taskforge` and `taskforge_test`.

Now try a small interactive session:
```bash
docker compose exec db psql -U dev -d taskforge
```
Inside `psql`, type each line (they end with `;`):
```sql
\l
\dt
create table hello (id serial primary key, msg text);
insert into hello (msg) values ('hi from postgres');
select * from hello;
\q
```
- `\l` lists databases, `\dt` lists tables (none yet), the three SQL lines create a table, add a row, and read it back, and `\q` quits. (The proper SQL lesson is on Day 8; today is just proof that it works.)

### 3.6 See it with your Day 1 tools
```bash
lsof -i :5432
nc -vz localhost 5432
```
- **Expect:** something like `com.docker…` listening on port 5432, and `nc` reporting `succeeded`. Port mapping in action.

### 3.7 Stopping, starting, and where the data lives
```bash
docker compose stop          # stop the container (data kept)
docker compose start         # start it again
docker compose down          # remove the container, KEEP the volume (data kept)
docker compose up -d         # recreate it: your `hello` table is still there
```
- **Check it yourself:** after `down` and `up -d`, run `docker compose exec db psql -U dev -d taskforge -c "select * from hello;"`. The row is still there, because the **volume** survived.
- ⚠️ **`docker compose down -v`** also **deletes the volume (your data)**. Only use it when you *want* a clean slate.
- Clean up the demo table:
```bash
docker compose exec db psql -U dev -d taskforge -c "drop table hello;"
```

### 3.8 If something goes wrong
| Problem | Fix |
|---|---|
| `Cannot connect to the Docker daemon` | Docker Desktop isn't running. Open it and wait |
| `port is already allocated` / "address already in use" on 5432 | Another Postgres is running (Homebrew or Postgres.app). Find it with `lsof -i :5432` and stop it. (Or change the mapping to `"5433:5432"`; then use port 5433 everywhere later) |
| `no matching manifest` / architecture errors | Make sure you installed the Docker version for your chip (Apple vs Intel) |
| Anything else for more than 10 minutes | Screenshot the error and ask me |

### Part 3 done when
- [ ] `docker run hello-world` worked
- [ ] `select version();` returned PostgreSQL 17 from your container
- [ ] You saw the `hello` table survive a `docker compose down` and `up -d`
- [ ] You can explain: image vs container, what a volume is, and what `5432:5432` means

---

# Part 4 · Python project: Log Analyzer (60 min)

A realistic little job: read a server log, turn it into numbers, and write a JSON report. It uses what you learned on Day 1 (functions, dicts, comprehensions, `Counter`, files, JSON, paths). **This is your proof that the Python is solid enough**, and it's something you *build*, not a drill.

**Time-box: 60 minutes.** If a function takes you 20 minutes, look at its solution at the bottom, close the file, and retype it.

### 4.1 Setup
Inside `python-fundamentals/`:
```bash
cd ~/backend-journey/python-fundamentals
mkdir -p log_analyzer
```
Create **`log_analyzer/access.log`** (paste this data exactly; **it contains one blank line on purpose**):
```
2026-11-01T10:00:01 GET /api/users 200 12ms
2026-11-01T10:00:02 POST /api/users 201 35ms
2026-11-01T10:00:03 GET /api/users/7 404 8ms
2026-11-01T10:00:05 GET /api/projects 200 20ms
2026-11-01T10:00:06 GET /api/projects 200 18ms
2026-11-01T10:00:09 POST /api/login 401 90ms

2026-11-01T10:00:10 POST /api/login 200 95ms
2026-11-01T10:00:12 GET /api/users 200 15ms
2026-11-01T10:00:15 DELETE /api/projects/3 500 250ms
2026-11-01T10:00:17 GET /api/projects 200 22ms
2026-11-01T10:00:20 GET /api/users/7 404 9ms
2026-11-01T10:00:21 GET /api/users 200 14ms
```
Each line is: `timestamp  METHOD  path  status  duration`. Does this look like the HTTP you learned? It's what a server writes for every request.

### 4.2 What to build
Write **`log_analyzer/analyze.py`** with four functions:

| Function | What it does |
|---|---|
| `parse_line(line: str) -> dict` | Returns `{"timestamp": str, "method": str, "path": str, "status": int, "duration_ms": int}`. *(Hint: `line.split()`; `"12ms".removesuffix("ms")`; `int(...)`.)* |
| `load_entries(path: Path) -> list[dict]` | Reads the file, **skips blank lines**, returns the parsed entries. *(Hint: `read_text().splitlines()`, and `line.strip()` to detect blanks.)* |
| `summarize(entries: list[dict]) -> dict` | Returns the dict described below |
| `write_report(summary: dict, path: Path) -> None` | Writes the summary as indented JSON (indent 2), creating parent folders. *(Hint: `path.parent.mkdir(...)`, `json.dumps`, `write_text`.)* |

**`summarize` returns a dict with these keys:**
- `total`: number of entries
- `status_counts`: `{status: how many}`. *(Hint: `Counter`.)*
- `method_counts`: `{method: how many}`
- `top_paths`: the **2 most common paths**, as a list of `(path, count)` tuples. *(Hint: `Counter(...).most_common(2)`.)*
- `error_count`: how many have status **≥ 400**
- `error_rate`: `error_count / total`, **rounded to 2 decimals**
- `avg_duration_ms`: average duration, **rounded to 2 decimals**
- `slowest`: the **whole entry** with the largest `duration_ms`. *(Hint: `max(entries, key=lambda e: e["duration_ms"])`.)*

**Work in this order, one function at a time, and print what you get after each step:**
1. `parse_line` on a single line from the log (try it in a tiny scratch script).
2. `load_entries`: print `len(entries)`. You should get 12.
3. `summarize`: add one key at a time and print it.
4. `write_report`: then open the JSON file it creates.

### 4.3 Your self-check
Create **`log_analyzer/check.py`** (type it; this is your acceptance test):
```python
import json
from pathlib import Path

from analyze import load_entries, parse_line, summarize, write_report

HERE = Path(__file__).parent
entries = load_entries(HERE / "access.log")
assert len(entries) == 12
assert entries[0] == {
    "timestamp": "2026-11-01T10:00:01", "method": "GET",
    "path": "/api/users", "status": 200, "duration_ms": 12,
}
assert parse_line("2026-11-01T10:00:02 POST /api/users 201 35ms")["duration_ms"] == 35

s = summarize(entries)
assert s["total"] == 12
assert s["status_counts"] == {200: 7, 201: 1, 404: 2, 401: 1, 500: 1}
assert s["method_counts"] == {"GET": 8, "POST": 3, "DELETE": 1}
assert s["top_paths"] == [("/api/users", 4), ("/api/projects", 3)]
assert s["error_count"] == 4
assert s["error_rate"] == 0.33
assert s["avg_duration_ms"] == 49.0
assert s["slowest"]["path"] == "/api/projects/3" and s["slowest"]["duration_ms"] == 250

out = HERE.parent / "scratch" / "report.json"
write_report(s, out)
data = json.loads(out.read_text(encoding="utf-8"))
assert data["status_counts"]["200"] == 7      # JSON keys are always strings
assert data["error_rate"] == 0.33
print("DAY 1 PROJECT: ALL CHECKS PASSED")
```
Run: `uv run python log_analyzer/check.py`
- **If it prints the final line**, you're done. If you see an `AssertionError`, the line number tells you which number is wrong: fix **your function**, never the asserts.

### Part 4 done when
- [ ] The final line prints
- [ ] Every function has type hints and a one-line docstring
- [ ] You opened `scratch/report.json` and can read what it says about the "server"
- [ ] Committed

*(If you're out of energy, skip this part and mark it `TODO`. It's on the Day 6 buffer list.)*

---

## Wrap-up (10 min)

**1. Explain without notes** (aloud, or 1–2 lines each)
1. What's the difference between a Docker **image** and a **container**?
2. What is a **volume**, and why does a database need one?
3. What does `ports: ["5432:5432"]` do?
4. What does `uv run fastapi dev hello.py` start, and what does auto-reload mean?
5. Where did `/docs` come from, and where did the **422 error** come from? (You wrote neither.)
6. Name three things from Days 1 to 4 that you saw working inside `hello.py`.

**2. Cheat sheet:** one line per question in `notes/00-python-cheatsheet.md` (your own words).

**3. Journal** (`journal.md`): `Did: … / Confused me: … / Tomorrow starts with: …`

**4. Commit and push** (VS Code Source Control: message, **Commit**, **Sync/Push**), or:
```bash
cd ~/backend-journey
git add .
git commit -m "day 5: fastapi hello, docker postgres, bruno, log analyzer"
git push
```
(Don't worry if Git says the `.venv` folders are ignored; that's correct.)

**Tomorrow (Day 6) is a buffer day.** Its to-do list (do what you feel like, in this order):
1. **Day 2, Parts 7–8:** the 10-minute HTTP cheat sheet is the most valuable bit.
2. Day 3: exception exercises 7–9.
3. Anything unfinished from today (usually the Log Analyzer).
4. Optional: Day 4's tests, debugging and logging.
If none of it appeals, **rest**. It's part of the plan. Then say **"Day 7 please"**: that's the start of Module 2 (FastAPI properly).

### Day 5 done when
- [ ] Your FastAPI server answered in the browser and in `curl`, and you saw `/docs`
- [ ] Postgres runs in Docker and you queried it
- [ ] Bruno sent a request
- [ ] Log Analyzer passes (or is marked `TODO`)
- [ ] Journal and commit done

---

# Quick reference (keep this)

**FastAPI**
```bash
cd ~/backend-journey/playground
uv run fastapi dev hello.py        # start the dev server (auto-reload) on http://127.0.0.1:8000
# /docs = interactive page · /openapi.json = API description
```

**Docker / Postgres** (run from `infra/`)
```bash
docker compose up -d                       # start in the background
docker compose ps                          # what's running
docker compose logs db | tail -5           # recent logs
docker compose exec db psql -U dev -d taskforge      # open the Postgres prompt
docker compose stop / start                # stop / start (data kept)
docker compose down                        # remove the container (data kept)
docker compose down -v                     # ⚠️ also deletes the data
```
**Inside psql:** `\l` databases · `\c name` connect · `\dt` tables · `\d table` describe a table · `\q` quit

**Ports to remember:** 8000 your FastAPI server · 5432 PostgreSQL · 6379 Redis (later)

---

# Solution: Log Analyzer (open only after 20 minutes of trying one function)

```python
import json
from collections import Counter
from pathlib import Path


def parse_line(line: str) -> dict:
    """Turn one log line into a dict."""
    timestamp, method, path, status, duration = line.split()
    return {
        "timestamp": timestamp,
        "method": method,
        "path": path,
        "status": int(status),
        "duration_ms": int(duration.removesuffix("ms")),
    }


def load_entries(path: Path) -> list[dict]:
    """Read the file, skip blank lines, parse the rest."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return [parse_line(line) for line in lines if line.strip()]


def summarize(entries: list[dict]) -> dict:
    """Compute the numbers we care about."""
    total = len(entries)
    error_count = sum(1 for e in entries if e["status"] >= 400)
    return {
        "total": total,
        "status_counts": dict(Counter(e["status"] for e in entries)),
        "method_counts": dict(Counter(e["method"] for e in entries)),
        "top_paths": Counter(e["path"] for e in entries).most_common(2),
        "error_count": error_count,
        "error_rate": round(error_count / total, 2),
        "avg_duration_ms": round(sum(e["duration_ms"] for e in entries) / total, 2),
        "slowest": max(entries, key=lambda e: e["duration_ms"]),
    }


def write_report(summary: dict, path: Path) -> None:
    """Write the summary as indented JSON, creating folders as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
```

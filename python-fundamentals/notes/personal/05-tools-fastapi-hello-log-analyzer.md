# 05 · Tools, FastAPI, Docker, PostgreSQL, and Log Analyzer · Personal Notes

> 🧭 **How to use this note:** Start with the map. Each section is self-contained for quick revision. The note keeps the practical commands and the technical “why” behind them; it also records what your Log Analyzer implementation and report show.

## 📚 Table of contents

- [60-second map](#60-second-map)
- [1. First FastAPI server](#1-first-fastapi-server)
- [2. Bruno: save and send requests](#2-bruno-save-and-send-requests)
- [3. Docker and PostgreSQL](#3-docker-and-postgresql)
- [4. Log Analyzer: pipeline and data model](#4-log-analyzer-pipeline-and-data-model)
- [5. Your implementation and report](#5-your-implementation-and-report)
- [6. Key connections to earlier days](#6-key-connections-to-earlier-days)
- [Common traps and practical fixes](#common-traps-and-practical-fixes)
- [One-page recall](#one-page-recall)
- [Recall drill](#recall-drill)

### Visual guide

| Mark | Meaning |
|---|---|
| 🧠 **Remember** | A core fact worth recalling |
| ⚠️ **Trap** | An easy-to-make mistake |
| 🔁 **Connection** | A link to an earlier concept |
| 🛠️ **Practical** | A command or implementation detail |

---

## 60-second map

Today connects Python and HTTP to working tools:

```text
Browser / curl / Bruno
          │ HTTP request
          ▼
FastAPI route → Python function → JSON response

FastAPI application ── network connection ── PostgreSQL
                                             inside Docker

access.log → parse lines → analyze entries → JSON report
```

- **FastAPI + Uvicorn:** an application framework plus an ASGI server that listens for HTTP requests.
- **Bruno:** a GUI client for creating, sending, and saving HTTP requests.
- **Docker image/container/volume:** template / running isolated instance / persistent data storage.
- **PostgreSQL:** relational database running in a container, reachable through a mapped host port.
- **Log Analyzer:** file input → structured Python data → aggregate statistics → JSON output.

---

## 1. First FastAPI server

### What runs when a request arrives?

```text
Client sends HTTP request
→ Uvicorn accepts it on a host/port
→ FastAPI matches method + path to a route
→ FastAPI parses and validates inputs
→ your Python function runs
→ FastAPI serializes the result and sends an HTTP response
```

- **FastAPI** handles routing, request parsing/validation, and response generation.
- **Uvicorn** is the ASGI server that listens for connections and runs the application.
- `127.0.0.1:8000` means this machine, port 8000.
- `fastapi dev` runs the development server and reloads after source changes.

### Set up and run

```bash
mkdir -p playground
cd playground
uv init --python 3.12
uv add "fastapi[standard]"
uv run fastapi dev hello.py
```

`uv init` creates project files; `uv add` adds FastAPI and its standard dependencies to the project; `uv run` runs in the project environment.

### The example API

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
    return {
        "received": item.model_dump(),
        "price_with_tax": round(item.price * 1.18, 2),
    }
```

### What the syntax is doing

| Code | Effect |
|---|---|
| `@app.get("/add")` | Registers the function as the handler for `GET /add` |
| `name: str` in `/greet/{name}` | Declares a path parameter |
| `excited: bool = False` | Declares an optional query parameter |
| `a: int, b: int` | FastAPI parses and validates query values as integers |
| `class Item(BaseModel)` | Pydantic model validates/represents JSON request data |
| `item.model_dump()` | Converts the validated model to a Python dictionary |
| `status_code=201` | Sets the successful response status |
| `return {...}` | FastAPI serializes the dictionary as JSON |

**FastAPI can generate behavior from type hints.** For example, `?a=2&b=x` produces a `422` validation response without hand-written validation code.

### Test the endpoints

| Request | Expected result |
|---|---|
| `GET /` | JSON message |
| `GET /greet/Asha` | `"Hello, Asha."` |
| `GET /greet/Asha?excited=true` | `"Hello, Asha!"` |
| `GET /add?a=2&b=3` | `{"result": 5}` |
| `GET /add?a=2&b=x` | `422`, invalid integer for `b` |
| `GET /add?a=2` | `422`, required query parameter `b` missing |
| `POST /add?a=2&b=3` | `405`, route exists but does not support POST |
| `GET /nope` | `404`, no matching route |
| `POST /items` with valid JSON | `201 Created` |
| `POST /items` with `"price": "abc"` | `422`, body validation error |

Useful URLs:

- `/docs` → interactive Swagger UI generated by FastAPI.
- `/openapi.json` → machine-readable OpenAPI description that `/docs` uses.

The server terminal logs each request and response status, e.g. `GET /add?a=2&b=3 HTTP/1.1 200 OK`.

### Raw HTTP with curl

```bash
curl -i "http://localhost:8000/add?a=2&b=3"
```

`-i` displays response headers and body. A typical response has a status line, headers, a blank line, then JSON body.

```bash
curl -i -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"pen","price":10}'
```

Expected: `201 Created` and `price_with_tax` of `11.8`.

🛠️ If port 8000 is already in use, inspect it with `lsof -i :8000`; stop the conflicting process or choose another port.

---

## 2. Bruno: save and send requests

Bruno is a graphical HTTP client. Like curl, it sends HTTP requests; unlike one-off terminal commands, it can save requests in a collection for reuse.

Typical setup:

1. Create a collection, e.g. `taskforge`.
2. Save it in the repository if you want its request files versioned.
3. Add a GET request to `http://localhost:8000/`.
4. Add a POST request to `/items`, select a JSON body, and send valid/invalid values.
5. Store the server base URL in a `local` environment, e.g. `baseUrl = http://localhost:8000`.
6. Refer to it as `{{baseUrl}}/items`.

**Why use an environment variable?** The same request can target local, test, or production environments by changing the base URL rather than editing every request.

Expected results match curl: valid item → `201`; invalid price → `422`. Bruno is a client; it does not replace FastAPI or Uvicorn.

---

## 3. Docker and PostgreSQL

### Docker concepts

| Term | Meaning |
|---|---|
| **Image** | A template/snapshot used to create containers, e.g. `postgres:17` |
| **Container** | A running, isolated instance of an image |
| **Volume** | Persistent storage kept outside the container's writable layer |
| **Docker Desktop** | On Mac, provides the Linux environment where Docker containers run |
| **Docker Compose** | Configuration and commands for one or more related containers |

An image is not the running database; the container is. A volume keeps database files when the container is stopped or removed.

### Compose configuration

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

- `services.db` defines the database service/container.
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` initialize the development database.
- `ports: ["5432:5432"]` means **host port : container port**. Connections to port 5432 on the Mac are forwarded to port 5432 in the container.
- `pgdata` is a named volume mounted where PostgreSQL stores its data.

⚠️ `dev`/`dev` is only acceptable for a local learning database. Never use these credentials for a publicly accessible production database.

### Start and inspect

Run from the directory containing the Compose file:

```bash
docker compose up -d
docker compose ps
docker compose logs db | tail -5
```

- `up -d` starts containers in the background.
- `ps` shows container state.
- Logs should eventually say the database is ready to accept connections.

### Connect and run basic SQL

```bash
docker compose exec db psql -U dev -d taskforge -c "select version();"
docker compose exec db createdb -U dev taskforge_test
docker compose exec db psql -U dev -l
```

`docker compose exec db ...` runs a command inside the running `db` container; `psql` is PostgreSQL's command-line client.

Interactive session:

```bash
docker compose exec db psql -U dev -d taskforge
```

Inside `psql`:

```sql
\l
\dt
create table hello (id serial primary key, msg text);
insert into hello (msg) values ('hi from postgres');
select * from hello;
\q
```

- `\l`: list databases
- `\dt`: list tables
- `\d table_name`: describe a table
- `\q`: quit
- SQL statements end with `;`; `psql` commands beginning with `\` are client meta-commands.

### Persistence: stop, remove, and delete data

```bash
docker compose stop       # stop container; data remains
docker compose start      # restart stopped container
docker compose down       # remove containers/network; named volume remains
docker compose up -d      # recreate containers, reusing the volume
```

**`docker compose down` keeps the named volume by default.** Database rows survive a container recreation because they live in `pgdata`, not only inside the container.

⚠️ **`docker compose down -v` deletes the named volume too.** That deletes the persistent database data. Use it only when you intentionally want a clean slate.

### Check connectivity and diagnose

```bash
lsof -i :5432
nc -vz localhost 5432
```

These check whether the mapped port has a listener and whether a TCP connection can be opened.

| Problem | Likely explanation |
|---|---|
| Cannot connect to Docker daemon | Docker Desktop is not running/ready |
| Port 5432 already allocated | Another local PostgreSQL process uses it; inspect with `lsof -i :5432` |
| Wrong architecture/image issue | Confirm Docker Desktop matches the Mac chip |
| Need an alternate host port | Map `"5433:5432"` and connect to host port 5433 |

---

## 4. Log Analyzer: pipeline and data model

### Goal

The Log Analyzer reads one server log entry per line and converts the file into a compact JSON report:

```text
log file → parse each line → list of dictionaries → aggregate statistics → JSON file
```

Each nonblank line has this shape:

```text
timestamp METHOD path status duration
2026-11-01T10:00:01 GET /api/users 200 12ms
```

Fields:

| Field | Python type | Example |
|---|---|---|
| timestamp | `str` | `"2026-11-01T10:00:01"` |
| method | `str` | `"GET"` |
| path | `str` | `"/api/users"` |
| status | `int` | `200` |
| duration_ms | `int` | `12` |

The sample has a blank line intentionally; `load_entries` should ignore it. There are 12 valid log entries.

### Four-function design

| Function | Responsibility |
|---|---|
| `parse_line(line)` | Split one line and convert status/duration to integers |
| `load_entries(path)` | Read text, split into lines, skip blanks, parse each record |
| `summarize(entries)` | Calculate counts, error metrics, frequent paths, and slowest record |
| `write_report(summary, path)` | Create output directories and write indented JSON |

Typical parsing operations:

```python
timestamp, method, path, status, duration = line.split()
status_code = int(status)
duration_ms = int(duration.removesuffix("ms"))
```

`split()` handles runs of whitespace and returns five fields. `removesuffix("ms")` removes the duration unit before integer conversion.

### Summary metrics

- `total`: number of parsed entries.
- `status_counts`: count by HTTP status code.
- `method_counts`: count by HTTP method.
- `top_paths`: two most frequently requested paths.
- `error_count`: entries with status `>= 400`.
- `error_rate`: `error_count / total`, rounded to two decimal places.
- `avg_duration_ms`: mean request duration, rounded to two decimals.
- `slowest`: complete entry with the largest duration.

**Why `Counter`?** `collections.Counter` counts occurrences from an iterable, e.g. methods or statuses. `.most_common(2)` returns the two most common `(value, count)` pairs.

### Expected analysis from the sample

```text
total            12
status_counts    200: 7, 201: 1, 404: 2, 401: 1, 500: 1
method_counts    GET: 8, POST: 3, DELETE: 1
top_paths        /api/users: 4, /api/projects: 3
error_count      4
error_rate       0.33
avg_duration_ms  49.0
slowest          DELETE /api/projects/3, status 500, duration 250 ms
```

The average is `588 ms / 12 = 49 ms`. The errors are the two `404`s, one `401`, and one `500`.

### Write JSON safely

```python
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
```

- `parents=True` creates missing parent directories.
- `exist_ok=True` allows the directory to already exist.
- Explicit UTF-8 encoding makes text file behavior predictable.
- Indentation makes the JSON easier to inspect.

Python JSON represents object keys as strings. Thus integer status keys such as `200` become `"200"` in the JSON document. Tuples such as `("/api/users", 4)` are serialized as JSON arrays.

---

## 5. Your implementation and report

Your current implementation is in [analyze.py](/Users/kxshrx/delulu/backend-journey/python-fundamentals/log_analyzer/analyze.py), with acceptance checks in [check.py](/Users/kxshrx/delulu/backend-journey/python-fundamentals/log_analyzer/check.py). The generated [report.json](/Users/kxshrx/delulu/backend-journey/python-fundamentals/scratch/report.json) records the sample summary.

Implementation details worth retaining:

- `parse_line` indexes the split fields and converts status/duration to integers.
- `load_entries` uses `splitlines()` and filters lines with `if line.strip()`, so the intentional blank line is skipped.
- `summarize` uses `Counter` for status, method, and path aggregation.
- Your implementation handles an **empty entry list**: rates/average become `0`, and `slowest` becomes `None`. The lesson’s simple solution assumes at least one entry and would divide by zero / fail at `max()` for an empty list.
- The in-memory summary keeps `Counter` objects. They behave as dictionary-like mappings and the JSON encoder writes them as JSON objects.
- `write_report` creates parent folders and writes indented JSON using a file context manager.
- The check verifies the 12 records, exact counts, top paths, error metrics, average, slowest entry, and JSON key conversion.

This is a useful implementation refinement: **define behavior for empty input rather than letting an accidental division-by-zero or `max()` error decide it.**

---

## 6. Key connections to earlier days

| Day/topic | Where it appears today |
|---|---|
| Networking: IP and ports | Uvicorn listens on `127.0.0.1:8000`; PostgreSQL is exposed on `5432` |
| HTTP request anatomy | FastAPI receives method, path, query, headers, and body |
| HTTP status codes | FastAPI returns `200`, `201`, `404`, `405`, and `422` |
| Type hints | FastAPI uses `int`, `str`, and `bool` annotations to parse/validate inputs |
| Decorators | `@app.get` and `@app.post` register route functions |
| Inheritance | `Item(BaseModel)` receives Pydantic behavior |
| Python files and JSON | Log Analyzer reads a text file and writes a JSON report |
| Comprehensions and `Counter` | Turn parsed records into counts |
| `Path` and files | Build paths and read/write files |

The framework is not magic: the route decorator registers functions, type annotations tell FastAPI what values to parse, and return values are serialized as HTTP responses.

---

## Common traps and practical fixes

- **FastAPI returns 422:** inspect the validation response; often a query parameter is missing/invalid or the JSON body has the wrong type.
- **404 vs 405:** `404` means no route matched; `405` means the path exists but not for that HTTP method.
- **Address already in use:** another process already listens on the port. Inspect with `lsof -i :PORT`.
- **Docker says daemon unavailable:** open Docker Desktop and wait for it to be ready.
- **Postgres data disappeared:** check whether `docker compose down -v` removed the volume.
- **Blank log line causes parsing failure:** filter empty/whitespace-only lines before calling `parse_line`.
- **`int("12ms")` fails:** remove the suffix first, then convert.
- **Integer keys appear as strings in report:** that is JSON object key behavior; decode and expect `"200"`.
- **Empty input breaks aggregates:** choose a documented policy; your code returns zero metrics and `slowest=None`.
- **Unsafe credentials:** `dev`/`dev` is a local-only example, not production configuration.

---

## One-page recall

| Topic | Recall sentence |
|---|---|
| FastAPI | Routes requests, validates inputs, and serializes responses |
| Uvicorn | ASGI server that listens and runs the app |
| `@app.get` | Registers a function for a method/path |
| Pydantic model | Validates and represents structured request data |
| `/docs` | Interactive docs generated from the OpenAPI schema |
| `422` | Request data could not pass validation |
| Bruno | Saves and sends HTTP requests through a GUI |
| Image | Docker template |
| Container | Running isolated instance of an image |
| Volume | Persistent storage outside the container lifecycle |
| `5432:5432` | Mac host port 5432 forwards to container port 5432 |
| `docker compose down` | Removes containers but normally preserves named volumes |
| `docker compose down -v` | Also deletes named volumes/data |
| Log Analyzer | Parse → load → summarize → write JSON |
| `Counter` | Counts occurrences; `most_common` ranks them |
| JSON object keys | Serialized as strings |
| Empty inputs | Handle explicitly rather than dividing by zero |

---

## Recall drill

Try without looking; revisit only the section you miss.

1. Describe the path from an HTTP request to a FastAPI response.
2. What do `@app.get`, a type hint, and a Pydantic model each contribute?
3. How do `404`, `405`, and `422` differ?
4. What do `/docs` and `/openapi.json` provide?
5. Distinguish Bruno from FastAPI/Uvicorn.
6. Explain image vs container vs volume.
7. Interpret `5432:5432` from the Mac's point of view.
8. Which Compose commands preserve or delete database data?
9. Name the Log Analyzer pipeline and the role of each function.
10. Why filter blank lines before parsing?
11. Why does JSON show a status key as `"200"` even if Python used `200`?
12. What special case does your implementation handle when there are no log entries?

# Day 2 · Monday 23 Nov: Networking B: HTTP in depth

> Module 1, Day 2 of 30 · about 4 hours including breaks · written for a **Mac**
> **Everything you need for today is in this file.** Don't look anything else up.
> Save it as `notes/days/day-02.md` in your `backend-journey` repo.
> This day has **no required coding**: only Terminal labs, the browser, and writing.

---

## How today works

| Part | Time | What |
|---|---|---|
| Check-in | 5 min | **Recall** 3 things from yesterday without looking, then write "today I'm done when…" in `journal.md` |
| **Recap** | 5 min | Where HTTP fits |
| **Part 1** | 35 min | The anatomy of a request and a response |
| **Part 2** | 40 min | Methods, URLs, and where data goes |
| Break | 5 min | Walk, water |
| **Part 3** | 25 min | Status codes |
| **Part 4** | 25 min | Headers |
| Break | 10 min | Eat something |
| **Part 5** | 25 min | State: cookies, sessions, tokens |
| **Part 6** | 15 min | REST in practice |
| **Part 7** | 10 min | CORS and HTTP versions (preview) |
| **Part 8** | 25 min | Consolidate: cheat sheet, the curl exam, the quiz |
| Wrap-up | 10 min | Commit and journal |

**Stop points.** Every part is complete on its own. **Floor rule (zero-energy day):** Recap + Part 1 + Part 2's tables = a counted day.

**How to get the most from this file**
1. **Read** a section, then **say it back** in one sentence.
2. **Run the labs.** Each has *what to run*, *what you should see*, *what to notice*. Most labs use `curl`, which you already used yesterday.
3. Keep `notes/networking.md` open and write one line whenever a lab surprises you.
4. The **Quick reference** at the end holds everything; you don't need to memorise.

**Two Terminal tabs.** Several labs need **Tab A** (a "server") and **Tab B** (a "client"). Open a new tab with `Cmd+T`. Stop anything running with `Ctrl+C`.

**When you're stuck:** 5 minutes → write `TODO` in your journal and move on · 20 minutes → ask an AI for a *hint* using the prompt in `01-fastapi-start-here.md`.

---

## Recap (5 min)

Yesterday you learned how a request **travels**: DNS finds the address, TCP opens the line, TLS locks it. Today is **what you actually say** once the line is open: **HTTP**.

In yesterday's journey table these are **step 5 (the request)** and **step 7 (the response)**. Almost everything you will build in FastAPI lives here: your API is a program that **reads HTTP requests and writes HTTP responses**.

```
 Client ───── HTTP request ─────▶ Server
        ◀──── HTTP response ─────
```
**HTTP is plain text.** A request is a few lines of text. A response is a few lines of text. That's it. Today you'll read them, write them by hand, and understand every part.

---

# Part 1 · The anatomy of a request and a response (35 min)

### 1.1 A request, line by line
```
POST /api/v1/projects?notify=true HTTP/1.1          ← 1. request line
Host: example.com                                   ← 2. headers (name: value)
Content-Type: application/json
Authorization: Bearer eyJhbGciOi...
Content-Length: 27
                                                    ← 3. a BLANK line ends the headers
{"name": "My first project"}                        ← 4. body (optional)
```
1. **Request line:** the **method** (what to do: `POST`), the **target** (path plus query string: `/api/v1/projects?notify=true`), and the **version** (`HTTP/1.1`).
2. **Headers:** extra information, one `Name: value` per line.
3. **A blank line** marks the end of the headers.
4. **Body:** the data you send (JSON, a form, a file). `GET` requests normally have none.

### 1.2 A response, line by line
```
HTTP/1.1 201 Created                                ← 1. status line: version, code, reason
Content-Type: application/json                      ← 2. headers
Content-Length: 45
Location: /api/v1/projects/12
                                                    ← 3. blank line
{"id": 12, "name": "My first project"}              ← 4. body
```
- **Status line:** the **status code** (`201`) is the machine-readable result; the reason phrase (`Created`) is just a label for humans.

### 1.3 Why there's a `Host` header
One server (one IP address) can host **many websites**. The `Host` header says *which one you want*. HTTP/1.1 requires it. Without it the server doesn't know which site to serve.

### 1.4 Small details worth knowing
- Lines end with `\r\n` (carriage return + line feed), and a blank line `\r\n\r\n` ends the headers.
- The server knows where the **body** ends from the **`Content-Length`** header (the number of bytes). Some responses use "chunked" transfer instead; same idea.
- Header **names are case-insensitive** (`content-type` = `Content-Type`).

### Lab 1: Read a real exchange (5 min)
```bash
curl -v --http1.1 https://example.com 2>&1 | grep -E '^[<>]'
```
- **Expect:** only the **request** lines (starting with `>`) and **response** lines (starting with `<`). You'll see `> GET / HTTP/1.1`, `> Host: example.com`, then `< HTTP/1.1 200 OK` and the response headers.
- **Notice:** you can now read every line. (`--http1.1` makes curl use the plain-text version. By default curl may use HTTP/2, which carries the same information in a binary format.)

### Lab 2: Be the server (10 min)
This is the best way to *see* HTTP. You'll play the server by hand using `nc` (netcat).

**Tab A** (the server). It will send a hand-written response to whoever connects, and print what it receives:
```bash
printf 'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 5\r\nConnection: close\r\n\r\nhello' | nc -l 8080
```
**Tab B** (the client):
```bash
curl -i -H "X-Test: 1" "http://localhost:8080/hello?x=1"
```
- **Expect in Tab B:** the response you wrote: `HTTP/1.1 200 OK`, the headers, then `hello`.
- **Expect in Tab A:** the **exact request curl sent**:
  ```
  GET /hello?x=1 HTTP/1.1
  Host: localhost:8080
  User-Agent: curl/…
  Accept: */*
  X-Test: 1
  ```
- **Notice:** the request line has the method, path *and the query string*; `Host` was added automatically; your custom `X-Test` header arrived. Nothing magic: **text in, text out.** Tab A exits by itself after one request.
- **Break it:** change `Content-Length: 5` to `Content-Length: 3` and run both tabs again. What does the body become? (The client reads exactly 3 bytes: `hel`. That's why the length header matters.)

### Lab 3: Be the client (5 min)
```bash
printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' | nc example.com 80
```
- **Expect:** a raw response: a status line, headers, and HTML (it may be `200`, or a `301` redirect to HTTPS; both are fine).
- **Now remove the Host header:**
```bash
printf 'GET / HTTP/1.1\r\nConnection: close\r\n\r\n' | nc example.com 80
```
- **Expect:** probably an error such as `400 Bad Request`. (Servers differ, but HTTP/1.1 requires `Host`.)
- **Notice:** you just spoke HTTP with no browser and no library.

**Part 1 done when**
- [ ] You can name the 4 parts of a request and the 4 parts of a response
- [ ] You can explain what `Host` and `Content-Length` are for
- [ ] You saw an exact request arrive in Tab A

---

# Part 2 · Methods, URLs, and where data goes (40 min)

### 2.1 Methods: the verb in the request
| Method | Meaning | Safe? | Idempotent? | Has a body? | Typical success |
|---|---|---|---|---|---|
| **GET** | read | yes | yes | no | 200 |
| **POST** | create something / run an action | no | **no** | yes | 201 (created) or 200 |
| **PUT** | **replace** the whole thing | no | yes | yes | 200 (or 204) |
| **PATCH** | change **part** of it | no | not guaranteed | yes | 200 |
| **DELETE** | remove | no | yes | rarely | 204 (no content) |
| HEAD | like GET but **only headers** | yes | yes | no | 200 |
| OPTIONS | "what may I do here?" (browsers use it for CORS) | yes | yes | no | 200/204 |

Two words matter:
- **Safe** = it doesn't change anything on the server. Browsers, crawlers and caches assume `GET` is safe. **Never make a GET change data.**
- **Idempotent** = doing it **twice has the same effect as doing it once**. Why you care: networks fail. If a request **times out**, did it arrive? If the method is idempotent you can **safely retry**. Retrying `DELETE /tasks/5` is fine (still gone). Retrying `POST /payments` might **charge twice**. That's why payment APIs use "idempotency keys".

**PUT vs PATCH:** `PUT /projects/5` with `{"name": "New"}` *replaces the whole project*, so missing fields are gone or reset. `PATCH /projects/5` with `{"name": "New"}` changes *only the name*. In practice, most APIs use `PATCH` for "edit these fields".

### 2.2 URLs and where data goes
```
https://api.example.com/v1/projects/5/tasks?status=todo&limit=20
 scheme   host           path (what thing)          query (how to list it)
```
A request can carry data in **four places**:

| Where | Use it for | Example |
|---|---|---|
| **Path** | *which* resource | `/projects/5` |
| **Query string** | *filter, sort, paginate, options* on a list | `?status=todo&limit=20&sort=-created_at` |
| **Body** | the data you're *sending* (create/update) | `{"name": "My project"}` |
| **Headers** | metadata and credentials | `Authorization: Bearer …` |

**Never put secrets (passwords, tokens) in a URL.** URLs end up in browser history, server logs and referrer headers.

**Percent-encoding.** URLs may only contain a safe set of characters, so others are encoded as `%` plus hex: a space is `%20`, `&` is `%26`, `?` is `%3F`. For example `title=hello world & more` becomes `title=hello%20world%20%26%20more`. Libraries do this for you; you only need to recognise it.

### 2.3 What's in the body, and `Content-Type`
The body is just bytes. The **`Content-Type`** header tells the receiver **how to read them**:

| `Content-Type` | Body looks like | Typical use |
|---|---|---|
| `application/json` | `{"name": "Asha"}` | **almost every API** |
| `application/x-www-form-urlencoded` | `username=asha&password=x` | simple HTML forms; **OAuth2 login in FastAPI** |
| `multipart/form-data` | several parts with boundaries | **file uploads** |
| `text/plain`, `text/html` | text / a web page | |

If you send JSON but forget the header (or send the wrong one), the server may reject it or misread it. The **`Accept`** header is the reverse: *what format I'd like back* (e.g. `Accept: application/json`).

### 2.4 Where this shows up in FastAPI (a preview)
| HTTP piece | FastAPI |
|---|---|
| path `/projects/5` | `@app.get("/projects/{project_id}")` with `project_id: int` |
| query `?limit=20` | a function parameter with a default: `limit: int = 20` |
| JSON body | a parameter typed as a Pydantic model |
| form body | `Form()` / `OAuth2PasswordRequestForm` |
| a header | `Header()` |
| a cookie | `Cookie()` |
| status code | `status_code=201`, or `raise HTTPException(404)` |

### Lab 4: The curl gauntlet, part 1 (15 min)
The practice API `jsonplaceholder.typicode.com` is a **fake** API: it answers like a real one but doesn't actually save anything. Run each line and write the **status code** in `notes/networking.md`:
```bash
curl -i https://jsonplaceholder.typicode.com/posts/1                       # GET one       → 200
curl -i "https://jsonplaceholder.typicode.com/posts?userId=1"              # GET a filtered list → 200
curl -i -X POST https://jsonplaceholder.typicode.com/posts \
     -H "Content-Type: application/json" \
     -d '{"title":"x","body":"y","userId":1}'                              # create        → 201
curl -i -X PUT https://jsonplaceholder.typicode.com/posts/1 \
     -H "Content-Type: application/json" \
     -d '{"id":1,"title":"x","body":"y","userId":1}'                       # replace       → 200
curl -i -X PATCH https://jsonplaceholder.typicode.com/posts/1 \
     -H "Content-Type: application/json" \
     -d '{"title":"only the title"}'                                       # partial       → 200
curl -i -X DELETE https://jsonplaceholder.typicode.com/posts/1             # delete        → 200
```
- **Notice:** the POST returns `201 Created` and the new object (with an `id`). The `\` at the end of a line just means "the command continues".

### Lab 5: Query strings and encoding (5 min)
```bash
curl -s "https://jsonplaceholder.typicode.com/posts?userId=1&_limit=2"
curl -v -G https://jsonplaceholder.typicode.com/posts --data-urlencode "title=hello world" 2>&1 | grep -E '^> GET'
```
- **Expect:** a JSON list of 2 posts; then a request line like `GET /posts?title=hello%20world HTTP/…`. That's the space being percent-encoded for you.

### Lab 6: Form vs JSON, seen from the server side (10 min)
**Tab A** (a server that only *prints* what it receives; it won't answer):
```bash
nc -l 8080
```
**Tab B:** send a **form** body:
```bash
curl -X POST http://localhost:8080/login -d "username=asha&password=x"
```
- **Expect in Tab A:** `POST /login HTTP/1.1`, a header `Content-Type: application/x-www-form-urlencoded`, a `Content-Length`, a blank line, then `username=asha&password=x`.
- Press `Ctrl+C` in **both** tabs (curl waits for an answer that never comes).
- Restart `nc -l 8080` in Tab A, then in Tab B send **JSON**:
```bash
curl -X POST http://localhost:8080/login -H "Content-Type: application/json" -d '{"username":"asha"}'
```
- **Expect:** now the header says `Content-Type: application/json` and the body is JSON. `Ctrl+C` both.
- **Notice:** the two requests differ in exactly two places: the `Content-Type` header and the shape of the body.

**Part 2 done when**
- [ ] You can explain safe vs idempotent, and why retries matter
- [ ] You can say what goes in the path vs the query vs the body vs the headers
- [ ] You saw both a form body and a JSON body arrive, and can name the header that tells them apart

---

# Part 3 · Status codes (25 min)

### 3.1 The five families
| Family | Meaning | Whose fault / what happened |
|---|---|---|
| **1xx** | informational | rarely seen |
| **2xx** | success | it worked |
| **3xx** | redirect | "look somewhere else" (the new address is in the `Location` header) |
| **4xx** | **client error** | **you** sent something wrong |
| **5xx** | **server error** | **the server** failed |

The 4xx/5xx split is vital: a **4xx** means "don't retry the same request; fix it". A **5xx** means "not your fault; maybe retry later".

### 3.2 The codes you must know
| Code | Name | Use it when |
|---|---|---|
| **200** | OK | a successful read or update |
| **201** | Created | a `POST` created something (also send a `Location` header) |
| **204** | No Content | success with nothing to return (a `DELETE`) |
| **301** / **302** | Moved Permanently / Found | a redirect (301 = permanent; 302 = temporary) |
| **304** | Not Modified | "your cached copy is still good" |
| **400** | Bad Request | the request is malformed (can't be parsed) |
| **401** | Unauthorized | **not logged in**, or bad/expired credentials |
| **403** | Forbidden | logged in, but **not allowed** |
| **404** | Not Found | it doesn't exist (or you're not allowed to know it exists) |
| **405** | Method Not Allowed | that URL doesn't support that method |
| **409** | Conflict | duplicate, or blocked by existing data |
| **422** | Unprocessable Content | valid format, but the **data fails validation** (FastAPI's default for bad input) |
| **429** | Too Many Requests | rate limit hit (often with a `Retry-After` header) |
| **500** | Internal Server Error | a bug in the server |
| **502** | Bad Gateway | a proxy got a bad answer from your app |
| **503** | Service Unavailable | overloaded or down for maintenance |
| **504** | Gateway Timeout | a proxy waited too long for your app |

**Rules of thumb**
- **Never return `200` with an error hidden inside the body.** Use the right code; clients and tools depend on it.
- **401 vs 403:** 401 = "who are you?" (you haven't proven it). 403 = "I know who you are, and no."
- **400 vs 422:** 400 = can't even parse it; 422 = parsed fine, but a field is invalid (e.g. an email without `@`).
- **404 for "not yours":** returning 404 instead of 403 for other people's data avoids revealing that it exists. You'll use this in the authorization module.

### Lab 7: Provoke status codes (10 min)
```bash
curl -i https://jsonplaceholder.typicode.com/posts/9999     # 404
curl -i http://github.com                                    # 301 + a Location header
curl -i https://api.github.com/user                          # 401: you're not logged in
```
- **Notice:** the 301's `Location:` header says where to go. `curl -iL http://github.com | head -30` follows it (`-L`) and shows both responses.
- **Print only the status of several URLs:**
```bash
for u in https://jsonplaceholder.typicode.com/posts/1 https://jsonplaceholder.typicode.com/posts/9999 https://api.github.com/user; do
  curl -s -o /dev/null -w "%{http_code}  $u\n" "$u"
done
```
- **Expect:** `200`, `404`, `401`.

### Lab 8: The 304 "not modified" trick (5 min)
```bash
curl -sI https://example.com
```
- Look for an **`etag:`** (or `last-modified:`) header and copy its value, including the quotes. **If there is none, skip this lab.**
```bash
curl -sI -H 'If-None-Match: "PASTE-THE-ETAG-HERE"' https://example.com
```
- **Expect:** `HTTP/… 304`. You said "I already have version X"; the server answered "still current" and sent **no body**. That's HTTP caching.

**Part 3 done when**
- [ ] You can sort any status code into its family and say whose fault it is
- [ ] You can explain 401 vs 403, and 400 vs 422
- [ ] You triggered a 404, a 301 and a 401

---

# Part 4 · Headers (25 min)

Headers are the **metadata** of HTTP. Grouped by purpose:

### 4.1 Request headers
| Header | What it says |
|---|---|
| `Host` | which site I want |
| `User-Agent` | what client I am (browser, curl, a Python library) |
| `Accept` | which formats I can handle |
| `Content-Type` | the format of the body I'm sending |
| `Content-Length` | how many bytes of body |
| `Authorization` | my credentials (`Bearer <token>` or `Basic <base64>`) |
| `Cookie` | cookies the browser stored for this site |
| `Origin` | which website (origin) the request comes from (CORS) |
| `If-None-Match` | "I already have this version" (caching) |

### 4.2 Response headers
| Header | What it says |
|---|---|
| `Content-Type` | the format of the body (`application/json; charset=utf-8`) |
| `Content-Length` | size of the body |
| `Set-Cookie` | "store this cookie" |
| `Location` | where to go (redirects; the URL of a newly created thing) |
| `Cache-Control` | how long and by whom this may be cached (`max-age=3600`, `no-store`) |
| `ETag` | a version label for caching |
| `WWW-Authenticate` | on a 401: how to authenticate (`Bearer`) |
| `Retry-After` | on 429/503: how long to wait |
| `Access-Control-Allow-Origin` | CORS: which websites may read this (Module 5) |

You can also invent **custom** headers (traditionally starting `X-`, like `X-Request-ID`).

### 4.3 Authentication headers
- **Basic:** `Authorization: Basic <base64 of "username:password">`. **Base64 is an encoding, not encryption**: anyone can decode it. Only safe inside HTTPS.
- **Bearer:** `Authorization: Bearer <token>`: "whoever *bears* (holds) this token is allowed in." This is what your API will use.

### 4.4 Caching in two sentences
`Cache-Control: max-age=3600` means "reuse this for an hour without asking me." `ETag` + `If-None-Match` means "ask me, but if nothing changed I'll answer `304` with no body", which saves bandwidth.

### Lab 9: Header detective (10 min)
```bash
curl -sI https://github.com
```
- Pick **5 headers** from the output. For each, write in your notes **what it does** (use the tables above; look up nothing else). If one is unknown, write "unknown".
- Open `https://github.com` in Chrome → DevTools (`Cmd+Option+I`) → **Network** → reload → click the first request → look at **Request Headers** and **Response Headers**. Find `accept`, `user-agent`, `content-type`.

### Lab 10: Base64 is not secret (5 min)
```bash
echo -n "asha:secret" | base64
echo 'YXNoYTpzZWNyZXQ=' | base64 -D
```
- **Expect:** `YXNoYTpzZWNyZXQ=` and then `asha:secret`. Anyone can read a Basic header. That's why you need HTTPS.
- **See it on the wire.** **Tab A:** `nc -l 8080`. **Tab B:** `curl -u asha:secret http://localhost:8080`. In Tab A find the `Authorization: Basic YXNoYTpzZWNyZXQ=` line. `Ctrl+C` both.

**Part 4 done when**
- [ ] You can name 5 request headers and 5 response headers and what they do
- [ ] You can explain Basic vs Bearer, and why base64 isn't security

---

# Part 5 · State: cookies, sessions, tokens (25 min)

### 5.1 The problem
HTTP is **stateless**: the server forgets you after every response. So how does a site know you're logged in on your next request? **Each request must carry proof of who you are.** There are two common ways.

### 5.2 Cookies
1. You log in. The server replies with a header: `Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax`
2. The browser **stores it**.
3. On **every later request to that site**, the browser **automatically** adds `Cookie: session=abc123`.

Cookie attributes you will meet again in the auth module:

| Attribute | What it does |
|---|---|
| `Max-Age` / `Expires` | how long it lives (without it: until the browser closes) |
| `Path` | only sent for URLs starting with this path |
| `Domain` | which site(s) get it |
| **`HttpOnly`** | JavaScript on the page **can't read it** (protects against XSS theft) |
| **`Secure`** | only sent over HTTPS |
| **`SameSite`** | `Strict`/`Lax`: not sent on requests triggered from other websites (protects against CSRF); `None`: sent everywhere (needs `Secure`) |

### 5.3 Sessions vs tokens (a preview, not the full story)
- **Session:** the cookie holds a random **session ID**; the **server remembers** who it belongs to (in memory or a database).
- **Token (e.g. JWT):** the client holds a **signed token** containing who you are. The server checks the signature and needs no memory. Sent in the `Authorization: Bearer …` header.

**The big difference between "cookie" and "header":** the browser sends cookies **automatically** (convenient, but another site can trick your browser into sending them: that's **CSRF**). A header is only sent when your own code adds it (so it isn't automatic), but then your JavaScript has to **store the token somewhere**, and a script injected into the page (XSS) could steal it. This trade-off is exactly why you'll build: a short-lived access token **held in memory** + a long-lived refresh token in an **HttpOnly cookie**. You'll study this properly in Module 3.

### Lab 11: A cookie round trip by hand (15 min)
**Tab A**: a server that sets a cookie:
```bash
printf 'HTTP/1.1 200 OK\r\nSet-Cookie: session=abc123; HttpOnly\r\nContent-Length: 2\r\nConnection: close\r\n\r\nhi' | nc -l 8080
```
**Tab B**: ask for it and **save the cookie** (`-c` writes a cookie jar file):
```bash
curl -i -c jar.txt http://localhost:8080
cat jar.txt
```
- **Expect:** the response includes `Set-Cookie: session=abc123; HttpOnly`. `jar.txt` contains a line with `session` and `abc123` (marked `#HttpOnly_localhost`).

Now the second request. **Tab A**: just print what arrives:
```bash
nc -l 8080
```
**Tab B**: send the saved cookie (`-b` reads the jar):
```bash
curl -b jar.txt http://localhost:8080/next
```
- **Expect in Tab A:** the request now contains `Cookie: session=abc123`. **That's the whole mechanism.** (`Ctrl+C` both tabs. Delete `jar.txt` after.)

### Lab 12: Cookies in your browser (10 min)
- Chrome → open a large site you're logged into → DevTools → **Application → Cookies**.
- Look at the columns: **Name, Value, Domain, Path, Expires, HttpOnly, Secure, SameSite.** Find one with **HttpOnly** ticked.
- In the **Console** type `document.cookie`. **Notice** that the HttpOnly cookie is *missing* from what JavaScript can read.

**Part 5 done when**
- [ ] You can explain how cookies turn stateless HTTP into a login
- [ ] You can say what `HttpOnly`, `Secure` and `SameSite` each do
- [ ] You saw `Cookie: session=abc123` arrive in Tab A

---

# Part 6 · REST in practice (15 min)

**REST** is a set of conventions for designing HTTP APIs. In short:
1. **URLs are nouns (resources)**, not verbs: `/projects`, not `/getProjects`.
2. The **method is the verb**: `GET` reads, `POST` creates, `PUT`/`PATCH` update, `DELETE` removes.
3. **Collections are plural**: `/projects` (the list), `/projects/5` (one item), `/projects/5/tasks` (its tasks).
4. Use **correct status codes** and **JSON** bodies.
5. **Stateless:** every request carries what the server needs.
6. Lists use **query parameters** for filtering, sorting and pagination: `?status=todo&limit=20&offset=40`.
7. **Version** your API in the URL: `/api/v1/...`.

| Operation | Method + URL | Success |
|---|---|---|
| Create | `POST /projects` | 201 + the new object |
| Read list | `GET /projects` | 200 |
| Read one | `GET /projects/5` | 200 (or 404) |
| Update part | `PATCH /projects/5` | 200 |
| Replace | `PUT /projects/5` | 200 |
| Delete | `DELETE /projects/5` | 204 |

**Common mistakes:** verbs in URLs (`/deleteTask?id=5`) · a `GET` that changes data · `200` with `{"error": …}` · singular/plural mixed up · inconsistent error format.

### Paper exercise: design TaskForge's URLs (10 min)
TaskForge is the API you'll build. On paper, for each purpose below, write the **method**, the **URL** (start with `/api/v1`) and the **success status**. Then compare with the answers at the bottom.
1. Log in
2. List my projects
3. Create a project
4. Get one project
5. Rename a project
6. Delete a project
7. Add a task to a project
8. List a project's tasks, only the ones with status "todo", 20 per page
9. Mark one task as done
10. Replace all the tags of a task

**Part 6 done when**
- [ ] You wrote all 10 before looking, and fixed your mistakes

---

# Part 7 · CORS and HTTP versions: a preview (10 min)

### 7.1 Origins
An **origin** = **scheme + host + port**. Two URLs are the **same origin** only if all three match.

| A | B | Same origin? |
|---|---|---|
| `https://app.com/a` | `https://app.com/b` | yes (only the path differs) |
| `https://app.com` | `http://app.com` | **no** (scheme) |
| `https://app.com` | `https://api.app.com` | **no** (host) |
| `http://localhost:3000` | `http://localhost:8000` | **no** (port) |

### 7.2 CORS in four sentences
Browsers have a rule: a web page may **not read responses from a different origin**, unless that server says it's allowed. Your frontend at `localhost:3000` calling your API at `localhost:8000` is *cross-origin*. The server opts in by sending `Access-Control-Allow-Origin: http://localhost:3000`. **The browser enforces this**, not the server: `curl` and Postman ignore it. You'll fix it in Module 5; for now just know that "CORS error" means *the browser blocked the response*, and the fix is on the **server**.

For some requests (for instance with an `Authorization` header or a JSON body) the browser first sends an **`OPTIONS` "preflight"** request to ask permission. Remember that word: you'll see it in DevTools later.

### 7.3 HTTP versions in one line
**HTTP/1.1:** one request at a time per connection (text). **HTTP/2:** many requests at once over one connection (binary). **HTTP/3:** the same idea over UDP/QUIC. Your code doesn't change across them.

---

# Part 8 · Consolidate: cheat sheet, the curl exam, the quiz (25 min)

### 8.1 Your HTTP cheat sheet (10 min)
In `notes/networking.md`, **without looking**, write one page:
1. The 4 parts of a request and of a response
2. The methods table (safe? idempotent?)
3. The 5 status families and the 12 codes you must know
4. Where data goes (path / query / body / headers)
5. The 8 headers you'll see most
6. How cookies make HTTP "remember" you
Then compare with this file and fix the gaps.

### 8.2 The curl exam (10 min)
Do these **using your cheat sheet, not the lab commands above**. Tick each when it works.
- [ ] 1. Fetch post number 5 and show the **status line and headers**
- [ ] 2. Fetch all posts of user 3 (a query string)
- [ ] 3. **Create** a post with a JSON body and see `201`
- [ ] 4. **Replace** post 2 (`PUT`)
- [ ] 5. **Partially update** post 2 (`PATCH`)
- [ ] 6. **Delete** post 2
- [ ] 7. Print **only the status code** for a post that doesn't exist (it should say `404`)
- [ ] 8. Start `nc -l 8080` in Tab A. From Tab B send a request with the header `X-Request-ID: abc` **and** `Authorization: Bearer t0k3n`, and confirm **both** appear in Tab A

### 8.3 The quiz (5 min to answer; check at the bottom)
Answer **in writing**, then check. Mark ✓/✗ and re-read the part for every ✗.

**Recall**
1. What are the 4 parts of an HTTP request? Of a response?
2. What is the `Host` header for?
3. Which methods are **safe**? Which are **idempotent**? Why does idempotency matter?
4. `PUT` vs `PATCH`?
5. Where does data go in a request, and what is each place for?
6. What does `Content-Type` do? What does `Accept` do?
7. 401 vs 403 vs 404?
8. 400 vs 422? What does 409 mean?
9. What do 301, 304, 429 and 502 each mean?
10. Why should you never return `200` for an error?
11. Basic vs Bearer authentication? Why isn't base64 security?
12. Describe how a cookie keeps you logged in (3 steps).
13. What do `HttpOnly`, `Secure` and `SameSite` each do?
14. What is an origin? Is `http://localhost:3000` the same origin as `http://localhost:8000`?
15. Who enforces CORS, the browser or the server?

**Scenarios**
16. A client times out sending `POST /orders`. Is it safe to just retry? What about `DELETE /orders/7`?
17. Your API returns `500` for a user's invalid email. What should it return, and why?
18. A user can see another user's project by changing the number in the URL. Which status should your API return for a project that isn't theirs, and why?
19. Your frontend gets a "CORS error" but the same request works in `curl`. Where's the problem?
20. Someone puts `?token=abc123` in a URL. Why is that a bad idea?

---

## Wrap-up (10 min)

1. **Journal** (`journal.md`): `Did: … / Confused me: … / Tomorrow starts with: …`
2. **Commit and push** (VS Code Source Control: message, **Commit**, **Sync/Push**), or:
   ```bash
   cd ~/backend-journey
   git add .
   git commit -m "day 2: HTTP in depth"
   git push
   ```
3. Delete the leftover lab file: `rm -f jar.txt`

**Tomorrow (Day 3):** the Python catch-up: **classes** (including inheritance and polymorphism, taken slowly), **errors** and **modules**. Tell me **"Day 3 please"**, plus anything that confused you today.

### Day 2 done when
- [ ] The HTTP cheat sheet is written and corrected
- [ ] The curl exam is ticked (8/8)
- [ ] Quiz answered and checked
- [ ] You can explain **"what is in an HTTP request, what comes back, and how does it remember me"** in two minutes
- [ ] Journal and commit done

---

# Quick reference (keep this)

**Request:** `METHOD /path?query HTTP/1.1` · headers · blank line · body
**Response:** `HTTP/1.1 CODE Reason` · headers · blank line · body

| Methods | Safe | Idempotent |
|---|---|---|
| GET, HEAD, OPTIONS | yes | yes |
| PUT, DELETE | no | yes |
| POST | no | no |
| PATCH | no | not guaranteed |

**Status:** 2xx ok · 3xx redirect · 4xx your fault · 5xx server's fault
`200` OK · `201` Created · `204` No Content · `301/302` redirect · `304` Not Modified · `400` Bad Request · `401` not authenticated · `403` not allowed · `404` not found · `405` wrong method · `409` conflict · `422` invalid data · `429` rate limited · `500` server bug · `502/503/504` proxy/availability problems

**Data goes in:** path (which) · query (filter/options) · body (the data) · headers (metadata/credentials)

**Content-Type:** `application/json` (APIs) · `application/x-www-form-urlencoded` (simple forms, OAuth2 login) · `multipart/form-data` (file uploads)

**Cookies:** `Set-Cookie` → browser stores → sends `Cookie` automatically. `HttpOnly` (no JS access) · `Secure` (HTTPS only) · `SameSite` (cross-site protection)

**Auth headers:** `Authorization: Bearer <token>` · `Authorization: Basic <base64(user:pass)>` (base64 ≠ encryption)

**Origin:** scheme + host + port · CORS = the browser blocks cross-origin reads unless the server allows them

**Commands from today:** `curl -i` · `curl -v --http1.1` · `curl -sI` · `curl -X METHOD -H "…" -d '…'` · `curl -G --data-urlencode` · `curl -c jar.txt / -b jar.txt` · `curl -u user:pass` · `curl -s -o /dev/null -w "%{http_code}"` · `nc -l 8080` · `printf '…' | nc host port` · `base64` / `base64 -D`

---

# Answers

### Paper exercise: TaskForge URLs
| # | Purpose | Method | URL | Success |
|---|---|---|---|---|
| 1 | Log in | POST | `/api/v1/auth/login` | 200 |
| 2 | List my projects | GET | `/api/v1/projects` | 200 |
| 3 | Create a project | POST | `/api/v1/projects` | 201 |
| 4 | Get one project | GET | `/api/v1/projects/{id}` | 200 |
| 5 | Rename a project | PATCH | `/api/v1/projects/{id}` | 200 |
| 6 | Delete a project | DELETE | `/api/v1/projects/{id}` | 204 |
| 7 | Add a task | POST | `/api/v1/projects/{id}/tasks` | 201 |
| 8 | List "todo" tasks, 20 per page | GET | `/api/v1/projects/{id}/tasks?status=todo&limit=20` | 200 |
| 9 | Mark a task done | PATCH | `/api/v1/projects/{id}/tasks/{task_id}` (body `{"status": "done"}`) | 200 |
| 10 | Replace a task's tags | PUT | `/api/v1/projects/{id}/tasks/{task_id}/tags` | 200 |

(Logging in is the one "action" that isn't a plain resource; that's a normal exception.)

### The curl exam: one possible set of commands
```bash
curl -i https://jsonplaceholder.typicode.com/posts/5
curl -s "https://jsonplaceholder.typicode.com/posts?userId=3"
curl -i -X POST https://jsonplaceholder.typicode.com/posts -H "Content-Type: application/json" -d '{"title":"t","body":"b","userId":1}'
curl -i -X PUT https://jsonplaceholder.typicode.com/posts/2 -H "Content-Type: application/json" -d '{"id":2,"title":"t","body":"b","userId":1}'
curl -i -X PATCH https://jsonplaceholder.typicode.com/posts/2 -H "Content-Type: application/json" -d '{"title":"new"}'
curl -i -X DELETE https://jsonplaceholder.typicode.com/posts/2
curl -s -o /dev/null -w "%{http_code}\n" https://jsonplaceholder.typicode.com/posts/9999
curl -H "X-Request-ID: abc" -H "Authorization: Bearer t0k3n" http://localhost:8080
```

### Quiz answers
1. **Request:** request line (method, target, version), headers, blank line, optional body. **Response:** status line (version, code, reason), headers, blank line, optional body.
2. It says **which website** on that server you want (one IP can host many sites). HTTP/1.1 requires it.
3. **Safe** (don't change anything): GET, HEAD, OPTIONS. **Idempotent** (same effect if repeated): GET, HEAD, OPTIONS, PUT, DELETE (not POST; PATCH isn't guaranteed). It matters because a **retry** after a timeout is only safe for idempotent methods.
4. **PUT** replaces the whole resource; **PATCH** changes only the fields you send.
5. **Path:** which resource. **Query:** filters, sorting, pagination, options. **Body:** the data you send. **Headers:** metadata and credentials.
6. **`Content-Type`** says what format the body I'm sending is in. **`Accept`** says which format I'd like back.
7. **401:** not authenticated (who are you?). **403:** authenticated but not allowed. **404:** not found (also used to hide that something exists).
8. **400:** the request is malformed or unparseable. **422:** parsed fine but the data fails validation. **409:** conflict (duplicate, or blocked by existing data).
9. **301:** moved permanently (redirect). **304:** not modified (use your cache). **429:** too many requests (rate limit). **502:** a proxy got a bad response from your app.
10. Clients, caches, monitoring and retries all rely on the code; a hidden error looks like success and breaks them.
11. **Basic:** `Authorization: Basic <base64(user:password)>`, sent with every request. **Bearer:** `Authorization: Bearer <token>`, whoever holds the token is allowed in. Base64 is an **encoding**, anyone can decode it; protection comes only from HTTPS.
12. (1) You log in; the server replies `Set-Cookie: session=…`. (2) The browser stores it. (3) The browser automatically sends `Cookie: session=…` on every later request to that site, so the server recognises you.
13. **HttpOnly:** JavaScript can't read the cookie. **Secure:** only sent over HTTPS. **SameSite:** restricts sending it on requests triggered from other websites (CSRF protection).
14. **Scheme + host + port.** No: the ports differ (3000 vs 8000), so they're different origins.
15. The **browser**. The server only declares what it allows (via `Access-Control-*` headers).
16. `POST /orders`: **not safe to just retry** (it might create a second order; you'd need an idempotency key or a check). `DELETE /orders/7`: **safe to retry** (the result is the same).
17. **422** (or 400): it's the **client's** data that's wrong, not a server bug. A 500 would mislead clients and monitoring into thinking your server is broken.
18. **404**, so that you don't reveal that the project exists (403 would confirm it).
19. On the **server**: it isn't sending the right CORS headers. `curl` doesn't enforce CORS; the browser does.
20. URLs are stored in browser history, server and proxy logs, and referrer headers, so the secret leaks. Put tokens in the `Authorization` header.

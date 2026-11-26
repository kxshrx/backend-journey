# 02 · HTTP In Depth · Personal Notes

> 🧭 **How to use this note:** Start with the 60-second picture and the bold lines. Each topic is self-contained; use the table of contents to revisit one question without rereading everything. Technical detail and the clarifications from your questions are kept here.

## 📚 Table of contents

- [60-second picture](#60-second-picture)
- [1. HTTP message anatomy](#1-http-message-anatomy)
- [2. Message framing: Content-Length, chunks, and transport layers](#2-message-framing-content-length-chunks-and-transport-layers)
- [3. HTTP versions](#3-http-versions)
- [4. Methods, safety, and idempotency](#4-methods-safety-and-idempotency)
- [5. URLs and where request data goes](#5-urls-and-where-request-data-goes)
- [6. Status codes](#6-status-codes)
- [7. Headers](#7-headers)
- [8. Authentication: Basic, Bearer, OAuth 2.0, and OIDC](#8-authentication-basic-bearer-oauth-20-and-oidc)
- [9. Cookies, sessions, tokens, and state](#9-cookies-sessions-tokens-and-state)
- [10. Caching and conditional requests](#10-caching-and-conditional-requests)
- [11. REST API design](#11-rest-api-design)
- [12. Origins and CORS](#12-origins-and-cors)
- [13. Debugging and practical examples](#13-debugging-and-practical-examples)
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
| 🛠️ **Practical** | A concrete example or debugging clue |

---

## 60-second picture

HTTP is the application-level conversation between a client and a server. For HTTPS, TLS protects that conversation while it travels.

```text
Client                                               Server
  |                                                    |
  | Request line + headers + blank line + optional body
  | -------------------------------------------------->|
  |                                                    |
  | Status line + headers + blank line + optional body
  |<-------------------------------------------------- |
```

**Request:** “Here is the resource/action I want, some context, and possibly data.”  
**Response:** “Here is the result, metadata, and possibly data.”

**Memory sentence:**  
**Method + target → headers → blank line → optional body.**  
**Status → headers → blank line → optional body.**

---

## 1. HTTP message anatomy

### Request

```http
POST /api/v1/projects?notify=true HTTP/1.1
Host: example.com
Content-Type: application/json
Accept: application/json
Content-Length: 28

{"name": "My first project"}
```

The four parts:

1. **Request line:** method, target (path and query), HTTP version
2. **Headers:** metadata, preferences, and sometimes credentials
3. **Blank line:** separates headers from the body
4. **Optional body:** data being sent

`GET` requests generally have no request body, but a **GET response can have a body**. Request and response bodies are separate.

### Response

```http
HTTP/1.1 201 Created
Content-Type: application/json
Content-Length: 38
Location: /api/v1/projects/12

{"id": 12, "name": "My first project"}
```

The four parts:

1. **Status line:** HTTP version, status code, human-readable reason phrase
2. **Headers**
3. **Blank line**
4. **Optional body**

The **status code** is what software uses. The reason phrase (`Created`) is a human-readable label.

### `Host` and HTTP/1.1

One IP address can serve multiple domain names. The `Host` header tells the server which hostname the client wants:

```http
GET / HTTP/1.1
Host: example.com
```

HTTP/1.1 requires a `Host` header. It is not the same thing as the destination IP: DNS and the connection identify where to connect; `Host` identifies the requested website on that server.

### Line endings and header rules

- HTTP/1.1 message lines conventionally end in `\r\n`.
- `\r\n\r\n` marks the end of the headers.
- Header names are **case-insensitive** (`content-type` and `Content-Type` mean the same thing).
- HTTP/2 and HTTP/3 require lowercase header names on the wire.

---

## 2. Message framing: Content-Length, chunks, and transport layers

### The key distinction

> ❓ **Does `Content-Length` tell TCP how much to send? No.** It is HTTP message-framing information. The HTTP receiver uses it to know how many body bytes belong to that message.

Who sets it depends on message direction:

| Message | Usually sets the header | Uses it to read the body |
|---|---|---|
| Request: client → server | Client | Server |
| Response: server → client | Server | Client |

`Content-Length` is a **byte count**, not a character count and not a limit on the amount someone is permitted to send.

```http
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 5

hello
```

The client reads five body bytes: `hello`.

If the server sends `hello` but declares `Content-Length: 3`, the HTTP client treats only `hel` as the response body. The remaining bytes do not belong to that response; with a persistent connection, extra bytes can confuse parsing of the next message. The server must frame the message correctly.

### Request and response framing are separate

For a request with a body:

```text
Client HTTP creates request and frames its body
→ TCP transports bytes
→ server TCP reassembles bytes
→ server HTTP reads the request body using HTTP framing
```

For the response, the same process happens in the opposite direction. **HTTP on each end understands message boundaries; TCP does not.**

In HTTP/1.1, a body can be framed using `Content-Length` or `Transfer-Encoding: chunked`. If neither framing mechanism indicates a request body, the request generally has no body. Responses can also use connection closure as a framing signal in applicable cases.

### HTTP/1.1 chunked transfer encoding

Chunked encoding lets an HTTP/1.1 sender stream a body without knowing the total length at the start. Each chunk has a hexadecimal byte count; a zero-sized chunk ends the body.

Conceptually:

```text
5\r\nhello\r\n
6\r\n world\r\n
0\r\n
\r\n
```

- `5` → next chunk has 5 bytes (`hello`)
- `6` → next chunk has 6 bytes (` world`)
- `0` → no more chunks

Chunking is **HTTP framing**, not TCP segmentation. It does not mean TCP sends each HTTP chunk in one matching segment.

### Three different units: HTTP, TLS, TCP

> ❓ **Are HTTP chunks, TLS records, TCP segments, and IP packets the same thing? No.** They are units at different layers and their boundaries need not line up.

| Layer | Unit / concept | Responsibility |
|---|---|---|
| HTTP | Message and body | Defines what belongs to a request or response |
| TLS | TLS records | Protects application data in transit |
| TCP | Byte stream; segments carry portions of it | Reliable, ordered transport between endpoints |
| IP | Packets/datagrams | Routes traffic across networks |

TCP may split a byte stream into segments, and the receiving TCP stack reassembles the ordered stream before the HTTP implementation reads it. One HTTP body may span many TCP segments; a segment may carry parts of different higher-layer units. Real segment sizes vary with MSS, network conditions, and implementation.

**Example:** if the HTTP body is 1,000 bytes and TCP carries it in five 200-byte segments, HTTP still sees one 1,000-byte body—not five HTTP messages.

If the header says `Content-Length: 500` while the sender actually supplies 1,000 body bytes, HTTP considers the first 500 bytes to be the body. The other bytes are not magically stopped by TCP; they are extra stream bytes and may be discarded on close or create parsing problems on a reused connection.

**Layer memory cue:**

- **HTTP:** Which bytes are this message's body?
- **TLS:** How are application bytes protected?
- **TCP:** How are bytes reliably delivered in order?
- **IP:** Where should packets be routed?

---

## 3. HTTP versions

**HTTP is not always plain text.** HTTP/1.1 is text-based; HTTP/2 and HTTP/3 use binary framing while preserving HTTP semantics.

| Feature | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| Transport | TCP | TCP | QUIC over UDP |
| Message format | Textual lines and headers; framed body | Binary frames; compressed headers (HPACK) | Binary frames over QUIC; QPACK headers |
| Multiple concurrent exchanges | Limited; commonly multiple connections | Multiplexes streams over one connection | Multiplexes streams over QUIC |
| Body completion | `Content-Length`, chunked encoding, or connection close as applicable | DATA frames and stream end (`END_STREAM`) | QUIC stream/frame completion |
| `Connection` header | Used in HTTP/1.1 | Connection-specific headers are not allowed | Connection-specific headers are not allowed |

### Why your `curl` output looked different

- In HTTP/1.1, a response may show `Transfer-Encoding: chunked`.
- HTTP/2 does **not** use HTTP/1.1 chunked transfer encoding. It carries data in DATA frames; frame/stream metadata signals completion.
- An HTTP/2 response can have no `Content-Length` and still have a clear end, indicated by the stream ending.
- HTTP/2 does not have the same textual status line on the wire; the status is represented using the `:status` pseudo-header internally.
- HTTP/2 header names are lowercase on the wire, and its header block is compressed.
- `curl -v` shows a **human-readable summary**, not every raw HTTP/2 binary frame. Frame-level inspection requires a protocol analyzer/debugger.

**Do not confuse:** HTTP/2 still has HTTP requests, responses, methods, status codes, and headers. Its wire framing is different; the application-level meaning is familiar.

---

## 4. Methods, safety, and idempotency

### Core methods

| Method | Intended use | Safe? | Idempotent? | Typical success |
|---|---|---:|---:|---|
| `GET` | Read a resource | Yes | Yes | `200` |
| `HEAD` | Like GET, but headers only | Yes | Yes | `200` |
| `POST` | Create or perform an action | No | No, by default | `201` or `200` |
| `PUT` | Replace a resource representation | No | Yes | `200` or `204` |
| `PATCH` | Partially modify a resource | No | Not guaranteed | `200` or `204` |
| `DELETE` | Remove a resource | No | Yes | `204` |
| `OPTIONS` | Ask what communication is supported | Yes | Yes | `200` or `204` |
| `TRACE` | Diagnostic loop-back request | Yes | Yes | Varies; often disabled |

### Safe is not the same as idempotent

> 🧠 **Safe:** Is the method intended to change server state?  
> 🧠 **Idempotent:** If I repeat the same request, is the intended server state the same as after one request?

“Safe” does not mean the server performs literally zero internal work: it may log or collect metrics. It means the client is asking to retrieve information, not to change application state.

| Method | Safe? | Idempotent? |
|---|---:|---:|
| `GET`, `HEAD`, `OPTIONS`, `TRACE` | Yes | Yes |
| `PUT`, `DELETE` | No | Yes |
| `POST` | No | No, by default |
| `PATCH` | No | Depends on the operation |

**Idempotent does not mean identical responses.** Repeated `DELETE /users/123` may return `204` first and `404` later, while the intended final state—user 123 is absent—remains the same.

### Why retries matter

If a client times out, it may not know whether the server processed the request:

```text
Client sends POST /payments
Server charges the card
Response gets lost
Client sees timeout and cannot tell whether the payment happened
```

Blindly retrying a non-idempotent `POST` can create a second payment. Payment APIs often support an **idempotency key**; the server must remember and enforce the key for retries to be safe.

- `PUT /users/123` with the same representation generally has the same intended effect when repeated.
- Repeating `DELETE /orders/7` leaves the order deleted; response codes may differ.
- `PATCH` is not inherently idempotent: “set balance to 500” is repeatable; “add 500” is not.

⚠️ **Correction worth remembering:** `PUT` is idempotent. `PATCH` may or may not be. Idempotency describes intended server effect, not whether the responses match exactly.

### `PUT` vs `PATCH`

- **PUT:** replace the whole resource representation. Omitted fields may be removed or reset, depending on the API's model.
- **PATCH:** apply a partial change to supplied fields.

```http
PUT /projects/5
Content-Type: application/json

{"name": "New name", "description": "Full replacement"}
```

```http
PATCH /projects/5
Content-Type: application/json

{"name": "New name"}
```

---

## 5. URLs and where request data goes

Example:

```text
https://api.example.com/v1/projects/5/tasks?status=todo&limit=20
```

| Part | Meaning |
|---|---|
| Scheme | `https` — protocol/security scheme |
| Host | `api.example.com` — requested host |
| Path | `/v1/projects/5/tasks` — resource/route |
| Query | `status=todo&limit=20` — options for selecting/representing results |

Request data commonly goes in four places:

| Location | Use it for | Example |
|---|---|---|
| **Path** | Which resource/route | `/projects/5` |
| **Query string** | Filters, sorting, search, pagination, or options | `?status=todo&limit=20&sort=-created_at` |
| **Body** | Data being sent, often for create/update | `{"name": "My project"}` |
| **Headers** | Message metadata, preferences, credentials | `Authorization: Bearer …` |

**Query parameters are not only for filters.** They can also represent sorting, pagination, search, and other optional behavior.

### Do not put secrets in URLs

Avoid `?token=abc123` or passwords in URLs. URLs can be retained in browser history, server/proxy logs, analytics, and `Referer` headers. Put credentials in an appropriate header or secure cookie instead.

### Percent-encoding

URLs have a restricted character set. Reserved or unsafe characters are encoded as `%` followed by hexadecimal bytes:

- space → `%20` (form encoding often represents it as `+`)
- `&` → `%26`
- `?` → `%3F`

For example, `title=hello world & more` is encoded so spaces and the literal ampersand are not mistaken for URL syntax. Client libraries usually encode values for you.

### Request body formats

The body is bytes. `Content-Type` tells the receiver how to interpret those bytes.

| Content-Type | Typical body | Common use |
|---|---|---|
| `application/json` | `{"name":"Asha"}` | APIs |
| `application/x-www-form-urlencoded` | `username=asha&password=x` | Traditional HTML forms; FastAPI OAuth2 password form |
| `multipart/form-data` | Multiple boundary-separated parts | File uploads and form fields |
| `text/plain`, `text/html` | Text or HTML | Plain text/web content |

#### Form URL-encoded vs JSON

```http
Content-Type: application/x-www-form-urlencoded

username=kishore&password=hello123
```

Fields are `key=value`, separated by `&`; special characters are encoded and spaces are commonly written as `+`.

```http
Content-Type: application/json

{"username": "kishore", "password": "hello123"}
```

JSON supports nested objects and arrays naturally. `multipart/form-data` is commonly used when a form includes files.

⚠️ Changing only `Content-Type` does not convert the body. If the body remains `username=Kishore&age=21` but the header says `application/json`, a JSON parser may reject it or interpret it incorrectly.

### `Content-Type` vs `Accept`

> ❓ **Content-Type describes what I send; Accept describes what I want back.**

```http
POST /users HTTP/1.1
Content-Type: application/json
Accept: application/xml

{"name": "Kishore"}
```

- `Content-Type: application/json` → request body is JSON.
- `Accept: application/xml` → client prefers an XML response.
- `Accept` is a preference, not an unconditional guarantee; the server may choose another representation or reject the request if it cannot provide the requested one.
- `Content-Type` can describe a request body **or** a response body.

---

## 6. Status codes

### The five families

| Family | Meaning |
|---|---|
| `1xx` | Informational |
| `2xx` | Successful |
| `3xx` | Redirect or use a cached representation |
| `4xx` | Client/request problem |
| `5xx` | Server or upstream-service problem |

### Common codes

| Code | Meaning | Useful distinction |
|---|---|---|
| `200 OK` | Successful request | Common for reads and updates with a body |
| `201 Created` | A resource was created | Often include `Location` for the new resource |
| `204 No Content` | Success, no response body | Common for deletion |
| `301 Moved Permanently` | Permanent redirect | New location in `Location` |
| `302 Found` | Temporary redirect | New location in `Location` |
| `304 Not Modified` | Cached representation is still valid | No response body; reuse cached copy |
| `400 Bad Request` | Malformed/unparseable request | The server cannot properly process its syntax |
| `401 Unauthorized` | Authentication is missing/invalid | “Who are you?”; often includes `WWW-Authenticate` |
| `403 Forbidden` | Authenticated/identified, but not permitted | “I know who you are; no.” |
| `404 Not Found` | Resource not found | Sometimes used to avoid disclosing that a protected resource exists |
| `405 Method Not Allowed` | Method is unsupported for this route | `Allow` may list supported methods |
| `409 Conflict` | Request conflicts with current state | E.g. duplicate or incompatible state |
| `422 Unprocessable Content` | Request understood but data fails validation | Common FastAPI validation response |
| `429 Too Many Requests` | Rate limit reached | May include `Retry-After` |
| `500 Internal Server Error` | Unexpected server failure/bug | Not a way to report ordinary invalid user input |
| `502 Bad Gateway` | Proxy/upstream returned an invalid response | Check proxy-to-app path |
| `503 Service Unavailable` | Service unavailable/overloaded/maintenance | May be temporary |
| `504 Gateway Timeout` | Proxy/upstream took too long | Check app latency and proxy timeout |

### Distinctions that often get mixed up

**401 vs 403**

- `401`: credentials absent, invalid, or expired; authentication has not succeeded.
- `403`: identity is known/authenticated, but access is not allowed.

**400 vs 422**

- `400`: malformed request or unable to parse it.
- `422`: request syntax/format is understood, but the supplied data fails validation (for example, an invalid email field).

**404 for someone else's resource**

An API may return `404` rather than `403` for a resource the current user does not own, to avoid revealing that it exists. This is a deliberate privacy policy; the API must enforce authorization either way.

**4xx vs 5xx and retries**

- A `4xx` generally means fix the request/credentials/permissions before retrying unchanged.
- A `5xx` can be temporary, but retry with backoff and only when the operation is safe/idempotent or protected with an idempotency mechanism.

⚠️ Do not return `200 OK` with an error hidden in the body. Clients, monitoring, caches, and retry logic rely on status codes.

---

## 7. Headers

Headers are metadata attached to an HTTP request or response. Some describe the message; others affect how it is processed.

### Request headers

| Header | Meaning |
|---|---|
| `Host` | Which hostname/site is requested |
| `User-Agent` | Client software's claimed identity |
| `Accept` | Response representation the client prefers |
| `Content-Type` | Format of this message's body |
| `Content-Length` | Number of body bytes, when used for framing |
| `Authorization` | Authentication credentials/token |
| `Cookie` | Cookies the browser is sending |
| `Origin` | Origin that initiated a browser request |
| `If-None-Match` | Conditional cache check using an ETag |
| `Access-Control-Request-Method` | Method the browser wants to use after preflight |
| `Access-Control-Request-Headers` | Headers the browser wants to send after preflight |

### Response headers

| Header | Meaning |
|---|---|
| `Content-Type` | Format of the response body |
| `Content-Length` | Number of response-body bytes, when used |
| `Set-Cookie` | Instructs browser to store/update a cookie |
| `Location` | Redirect target or newly created resource location |
| `Cache-Control` | Caching rules, e.g. `max-age=3600`, `no-store` |
| `ETag` | Validator/version identifier for a representation |
| `WWW-Authenticate` | Authentication challenge, commonly with `401` |
| `Retry-After` | How long to wait, e.g. after `429` or `503` |
| `Access-Control-Allow-Origin` | Origins the browser may allow to read the response |
| `Access-Control-Allow-Methods` | Methods allowed by CORS policy |
| `Access-Control-Allow-Headers` | Request headers allowed by CORS policy |
| `Access-Control-Allow-Credentials` | Whether credentialed browser requests are allowed |

Custom headers are also common, e.g. `X-Request-ID`. The historical `X-` prefix is a convention, not a requirement for custom metadata.

### `User-Agent` is not identity

It gives the server information about the claimed client (browser, OS, curl, etc.). A server may use it for compatibility, analytics, or rate-limiting decisions.

⚠️ **It is client-supplied and can be changed.** A curl command can claim to be Chrome. Never use `User-Agent` as proof of identity or authorization.

### Basic authentication

Basic authentication encodes `username:password` with Base64:

```text
username:password
→ Base64
→ Authorization: Basic <encoded-value>
```

**Base64 is encoding, not encryption.** Anyone who obtains the header can decode it. Use Basic only over HTTPS; TLS protects the header in transit, but Basic still sends the password-derived credential on each request.

### Bearer authentication

```http
Authorization: Bearer <access-token>
```

“Bearer” means whoever possesses the token can present it. A bearer token is **not inherently encrypted**; HTTPS protects it in transit. Treat it like a secret: a stolen valid token may be usable by someone else until it expires or is revoked.

If the token is a JWT, its payload is commonly readable; a signature can help detect modification, but a signature does not encrypt the token.

---

## 8. Authentication: Basic, Bearer, OAuth 2.0, and OIDC

### Authentication vs authorization

| Concept | Question |
|---|---|
| **Authentication** | Who are you? |
| **Authorization** | What are you allowed to do? |

A valid token can identify a user without granting access to every resource. The server still checks authorization for the requested resource.

### Do not mix up Basic, Bearer, and OAuth

These are not three interchangeable authentication methods:

- **Basic:** HTTP authentication scheme that sends Base64-encoded username/password.
- **Bearer:** HTTP authentication scheme for presenting a token.
- **OAuth 2.0:** authorization framework describing how clients obtain and use access tokens; OAuth flows commonly use Bearer tokens to call APIs.
- **OpenID Connect (OIDC):** identity layer built on OAuth 2.0, used when the client needs to establish the user's identity/login.

Typical simplified flow:

```text
User authorizes/signs in with identity provider
→ client obtains an access token
→ client sends Authorization: Bearer <token>
→ API validates token and checks its permissions/scopes
```

Access tokens are often short-lived; refresh-token behavior depends on the system. Scopes can restrict what a token permits.

---

## 9. Cookies, sessions, tokens, and state

### HTTP is stateless

HTTP does not automatically remember that two requests came from the same logged-in user. Each request must carry information that allows the server to associate it with the relevant identity/session.

### Cookie round trip

1. After login, server sends `Set-Cookie`.
2. Browser stores the cookie, subject to its attributes and browser rules.
3. Browser automatically sends a matching `Cookie` on later requests.

```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc789; HttpOnly; Secure; SameSite=Lax; Path=/
```

Later:

```http
GET /orders HTTP/1.1
Host: shop.example.com
Cookie: session_id=abc789
```

The cookie often holds a random **session ID**, not the user's password or full profile. The server looks up that ID in its session store.

### Cookie attributes

| Attribute | Effect |
|---|---|
| `Max-Age` / `Expires` | Cookie lifetime; without an explicit lifetime it is generally a session cookie |
| `Path` | URL path scope for sending the cookie |
| `Domain` | Host/domain scope |
| `HttpOnly` | Prevents page JavaScript from reading the cookie through `document.cookie`; does not stop the browser sending it |
| `Secure` | Browser sends it only over HTTPS |
| `SameSite=Strict` / `Lax` | Restricts sending in some cross-site contexts; helps reduce CSRF |
| `SameSite=None` | Allows cross-site sending and requires `Secure` in modern browsers |

SameSite helps mitigate CSRF but should not be treated as a complete substitute for appropriate CSRF protections.

### Session vs token

| Approach | What client holds | Where identity/state is checked |
|---|---|---|
| Server-side session | Random session ID, commonly in a cookie | Server looks up session in memory/database |
| Token | Token, often sent in `Authorization: Bearer …` | Server validates token; a self-contained signed token may avoid a per-request session lookup |

“Stateless token” is a design choice, not a guarantee that every token is self-contained or that the system stores no state. Revocation, refresh, and authorization can still require server-side state.

### Cookie vs Authorization header: trade-offs

- Browsers usually attach matching cookies automatically. This is convenient, but also creates CSRF considerations because another site may cause a browser to send cookies in some situations.
- A Bearer header is normally added explicitly by application code, so it is not automatically attached to every matching request. If JavaScript stores the token where injected scripts can read it, XSS can steal it.
- `HttpOnly` prevents JavaScript from reading that cookie; it does not prevent XSS from making requests as the user from within the page.
- One common architecture uses a short-lived access token kept in memory plus a longer-lived refresh token in an `HttpOnly`, `Secure` cookie. It is a design pattern, not a universal rule.

Do not assume a real request must send both a session cookie and a Bearer token. They are separate credential mechanisms; an application chooses an architecture that fits its clients and security requirements.

---

## 10. Caching and conditional requests

### `Cache-Control`

```http
Cache-Control: max-age=3600
```

The response can be reused from cache for up to 3,600 seconds, subject to the caching rules. `no-store` tells caches not to store the response.

### ETag and `If-None-Match`

An **ETag** is a validator identifying a particular representation/version:

```http
HTTP/1.1 200 OK
ETag: "product-v1"
Content-Type: application/json

{"id": 123, "name": "MacBook"}
```

The client stores the response and later asks whether it is still current:

```http
GET /products/123 HTTP/1.1
If-None-Match: "product-v1"
```

- If unchanged: server returns `304 Not Modified`, usually without the representation body; client reuses its cached copy.
- If changed: server returns `200 OK` with the new representation and validator.

`Last-Modified` / `If-Modified-Since` provide another conditional validation mechanism.

---

## 11. REST API design

REST is a set of API design constraints/conventions. Common practical conventions:

1. Use **nouns/resources** in paths: `/projects`, not `/getProjects`.
2. Use HTTP **methods** for operations: GET, POST, PUT/PATCH, DELETE.
3. Use plural collection names: `/projects`, `/projects/5`, `/projects/5/tasks`.
4. Use appropriate status codes and a consistent representation, often JSON.
5. Keep requests self-contained: include what the server needs to process each request.
6. Use query parameters for filtering, sorting, search, and pagination.
7. Version APIs consistently, often in the path: `/api/v1/...`.

| Operation | Method + URL | Typical success |
|---|---|---|
| Create project | `POST /api/v1/projects` | `201` + created object, often `Location` |
| Read project list | `GET /api/v1/projects` | `200` |
| Read one project | `GET /api/v1/projects/5` | `200` or `404` |
| Partially update | `PATCH /api/v1/projects/5` | `200` or `204` |
| Replace | `PUT /api/v1/projects/5` | `200` or `204` |
| Delete | `DELETE /api/v1/projects/5` | `204` |
| List filtered tasks | `GET /api/v1/projects/5/tasks?status=todo&limit=20` | `200` |

Login is commonly represented as an action endpoint such as `POST /api/v1/auth/login`; action-like endpoints are a normal exception to noun-style resource paths.

Avoid:

- verbs embedded in resource paths (`/deleteTask?id=5`)
- state-changing `GET` endpoints
- `200 OK` with an error hidden in the body
- inconsistent singular/plural or error formats

FastAPI mapping preview:

| HTTP data | FastAPI pattern |
|---|---|
| `/projects/{project_id}` | Path parameter |
| `?limit=20` | Query parameter |
| JSON body | Pydantic model parameter |
| Form body | `Form()` / `OAuth2PasswordRequestForm` |
| Header | `Header()` |
| Cookie | `Cookie()` |
| Response status | `status_code=201` or `HTTPException(404)` |

---

## 12. Origins and CORS

### Origin

**Origin = scheme + host + port.** The path does not count.

| URL A | URL B | Same origin? |
|---|---|---|
| `https://app.com/a` | `https://app.com/b` | Yes |
| `https://app.com` | `http://app.com` | No: scheme differs |
| `https://app.com` | `https://api.app.com` | No: host differs |
| `http://localhost:3000` | `http://localhost:8000` | No: port differs |

`shop.example.com` and `api.example.com` are different origins even though they share a registered domain.

### What CORS does

CORS (Cross-Origin Resource Sharing) is a **browser-enforced policy** governing whether JavaScript from one origin may read a response from another origin.

Example:

```text
Page origin: https://shop.example.com
API origin:  https://api.example.com
```

The browser sends an `Origin` header. The API can respond with:

```http
Access-Control-Allow-Origin: https://shop.example.com
```

The browser checks the policy before making the response available to page JavaScript.

> ❓ **Why can the same request work in curl but fail in the browser?** `curl` does not enforce browser CORS rules. CORS is not authentication and is not a general firewall; the server may receive/process a request even if the browser later blocks JavaScript from reading the response.

### Preflight

For some cross-origin requests (for example, certain requests using `Authorization` or JSON content), the browser first asks permission with an `OPTIONS` preflight:

```http
OPTIONS /orders HTTP/1.1
Origin: https://shop.example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: authorization,content-type
```

The server may answer with `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`. If allowed, the browser sends the actual request.

### CORS with cookies/credentials

For a cross-origin browser request that includes cookies:

- frontend code must opt into sending credentials where required
- server must explicitly allow credentials
- `Access-Control-Allow-Origin: *` cannot be used with credentialed CORS responses; the allowed origin must be explicit

**Keep these separate:**

- **Authentication:** Who is the caller?
- **Authorization:** What may that caller access?
- **CORS:** May browser JavaScript from this origin read the cross-origin response?

CORS does not protect an API from curl, server-side clients, or other non-browser callers.

---

## 13. Debugging and practical examples

### Read an HTTP/1.1 exchange

```bash
curl -v --http1.1 https://example.com 2>&1 | grep -E '^[<>]'
```

`>` lines are request details and `<` lines are response details. `--http1.1` makes the exchange easier to inspect as text.

### Inspect response headers

```bash
curl -sI https://example.com
```

### Send JSON

```bash
curl -i -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"name":"Asha"}'
```

### Send form data

```bash
curl -i -X POST http://localhost:8080/login \
  -d "username=asha&password=x"
```

With `-d`, curl typically uses `application/x-www-form-urlencoded` unless configured otherwise.

### Encode query values

```bash
curl -G https://api.example.com/products \
  --data-urlencode "title=hello world"
```

`-G` puts the supplied data in the query string; `--data-urlencode` encodes it.

### Cookie jar round trip

```bash
curl -i -c jar.txt http://localhost:8080
curl -b jar.txt http://localhost:8080/next
```

- `-c` saves received cookies to a jar.
- `-b` sends cookies from a jar.
- Remove the temporary jar after a lab; it may contain session credentials.

### Print only the status code

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://api.example.com/users/123
```

### Hand-written HTTP

HTTP/1.1's text format makes it possible to send a request with netcat:

```bash
printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' \
  | nc example.com 80
```

The blank line terminates the headers. Without the required HTTP/1.1 `Host`, servers commonly return `400 Bad Request`.

### Common diagnosis

| Symptom | Likely HTTP/network layer |
|---|---|
| `301`/`302` | Redirect; inspect `Location` |
| `401` | Missing/invalid authentication |
| `403` | Authenticated but not permitted |
| `404` | Route/resource unavailable or intentionally concealed |
| `422` | Input validation failed |
| `429` | Rate limit; inspect `Retry-After` |
| `502`/`503`/`504` | Proxy/upstream availability or timeout |
| Browser CORS error but curl succeeds | Browser CORS policy/response headers |
| Body seems truncated | Check HTTP framing/declared `Content-Length`, transfer mode, and connection |
| HTTP/2 has no `Content-Length` | Normal; DATA frames and stream end can frame the body |

---

## Most important doubts, resolved

1. **Who sets `Content-Length`?** The sender of that HTTP message. For a request, normally the client; for a response, the server. The receiver uses it to frame/read the body.
2. **Does a smaller `Content-Length` stop TCP from sending extra bytes?** No. TCP only transports bytes. HTTP interprets the declared length; extra bytes can be discarded or break parsing on a reused connection.
3. **Is the server or client reading the response length?** The client reads a response and uses the server's `Content-Length`. The server reads a request and uses the client's `Content-Length`.
4. **Does HTTP/2 need chunked encoding or `Content-Length` to know when a body ends?** No. HTTP/2 uses DATA frames and stream-end metadata (`END_STREAM`). It does not use HTTP/1.1 chunked transfer encoding.
5. **Are TCP segments HTTP fragments?** No. TCP transports a byte stream in segments. HTTP message boundaries are determined at the HTTP layer.
6. **Are HTTP body size, TLS record size, TCP segment size, and IP packet size interchangeable?** No. These are different layers; the boundaries/sizes do not have to match.
7. **Does `Content-Type` say what I want back?** No. It describes the message body being sent (request or response). `Accept` describes the response format the client prefers.
8. **Does `Accept` guarantee the server returns that format?** No. It expresses a preference; server capabilities and negotiation determine the result.
9. **Is `PUT` idempotent?** Yes, by intended effect. Repeating the same replacement should leave the resource in the same intended state.
10. **Is `PATCH` idempotent?** Not inherently. It depends on the patch operation; “set value” can be idempotent, “increment value” is not.
11. **Does idempotent mean repeated responses are identical?** No. It means the intended server state is the same after one or more identical requests.
12. **Are query parameters only for filtering?** No. They can control sorting, pagination, search, and other optional behavior.
13. **Does GET have a body?** A GET request generally does not need one; its response may contain a body.
14. **Are form fields separated by spaces?** No. URL-encoded fields are `key=value` pairs separated by `&`; special characters are encoded.
15. **Is User-Agent trustworthy?** No. A client can claim to be any browser. It is descriptive, not authentication.
16. **Are Basic, Bearer, and OAuth 2.0 the same kind of thing?** No. Basic and Bearer are HTTP auth schemes; OAuth 2.0 is a token authorization framework. OIDC adds identity/login semantics.
17. **Does Bearer mean encrypted token?** No. It means possession is used to present the credential. HTTPS protects it in transit; JWT content may remain readable.
18. **Does CORS authenticate users or block curl?** No. CORS is enforced by browsers to control JavaScript access to cross-origin responses. It is not API authentication.
19. **Can two subdomains be same-origin because they share a domain?** No. Origin requires the exact scheme, host, and port to match.
20. **If CORS says `*`, can anyone read protected user data?** Not by that fact alone. CORS is not authorization; the API must still authenticate and authorize access. Wildcard origin is also not allowed for credentialed CORS.

---

## One-page recall

| Topic | Recall sentence |
|---|---|
| HTTP request | Method + target + version; headers; blank line; optional body |
| HTTP response | Version + status; headers; blank line; optional body |
| `Host` | Which site name should this server serve? |
| `Content-Length` | How many bytes belong to this body; receiver uses it |
| HTTP vs TCP | HTTP frames messages; TCP delivers an ordered byte stream |
| Chunked vs segments | Chunked is HTTP/1.1 framing; TCP segments are transport units |
| HTTP/2 framing | Binary frames, multiplexed streams, end-of-stream metadata |
| Safe | Intended not to change application state |
| Idempotent | Repetition has the same intended effect |
| `PUT` vs `PATCH` | Replace vs partial change |
| Path/query/body/headers | Which resource / how to select / data / metadata & credentials |
| `Content-Type` | Format of this message's body |
| `Accept` | Response format client prefers |
| `401` vs `403` | Not authenticated vs not allowed |
| `400` vs `422` | Malformed vs parsed but invalid data |
| Basic | Base64-encoded username/password; not encryption |
| Bearer | Possession of token grants the token's permitted access |
| OAuth 2.0 / OIDC | Authorization framework / identity layer |
| Cookie | Browser-stored value, automatically sent when cookie rules match |
| Session | Server-side state looked up by session ID |
| ETag | Version validator; client sends it via `If-None-Match` |
| CORS | Browser policy for reading cross-origin responses, not authentication |
| Origin | Scheme + host + port |

---

## Recall drill

Try without looking. If one answer is missing, revisit only its section.

1. Recite the four parts of a request and response.
2. Who sets `Content-Length` on a request? Who sets it on a response? Who reads each?
3. Explain why TCP cannot see or obey an HTTP `Content-Length`.
4. Distinguish chunked encoding, HTTP/2 DATA frames, TLS records, and TCP segments.
5. Explain safe vs idempotent, and why `PUT` and `PATCH` differ.
6. Identify path, query, body, and headers in a sample request.
7. Explain `Content-Type` vs `Accept`.
8. Explain `401` vs `403`, and `400` vs `422`.
9. Explain Basic vs Bearer vs OAuth 2.0 vs OIDC.
10. Explain the `Set-Cookie` → browser storage → `Cookie` round trip.
11. Explain ETag, `If-None-Match`, and `304`.
12. Explain why a browser CORS error may not happen in curl.
13. State an origin and why `localhost:3000` differs from `localhost:8000`.
14. Name two reasons not to put a token in a URL.

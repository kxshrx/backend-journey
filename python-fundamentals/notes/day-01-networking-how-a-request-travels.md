# Day 1 · Sunday 22 Nov: Networking A: How a request travels

> Module 1, Day 1 of 30 · about 4 hours including breaks · written for a **Mac**
> **Everything you need for today is in this file.** Don't look anything else up.
> Save it as `notes/days/day-01.md` in your `backend-journey` repo.

---

## How today works

| Part | Time | What |
|---|---|---|
| Check-in | 5 min | Write "today I'm done when…" in `journal.md` |
| **The big picture** | 15 min | One mental model for the whole day |
| **Part 1** | 35 min | Addresses: IP, ports, localhost |
| **Part 2** | 35 min | Names: DNS |
| Break | 5 min | Walk, water |
| **Part 3** | 40 min | The pipes: packets, TCP, UDP, latency |
| **Part 4** | 35 min | The lock: TLS and HTTPS |
| Break | 10 min | Eat something |
| **Part 5** | 20 min | The middlemen and the whole journey |
| **Part 6** | 35 min | Put it in your own words, code exercises, quiz |
| Wrap-up | 10 min | Cheat sheet, journal, commit |

**Stop points.** Every part is complete on its own. On a heavy day you can stop after any part.
**Floor rule (zero-energy day):** the big picture + Part 1 = a counted day.

**How to learn from this file** (it works better than just reading):
1. **Read** a section, then **close your eyes and say it back** in one sentence.
2. **Run every lab.** Each one has *what to run*, *what you should see*, and *what to notice*.
3. Keep a file `notes/networking.md` open. Whenever a lab surprises you, write one line.
4. Don't memorise. If you forget something, the **Quick reference** at the end has it.

**When you're stuck:** 5 minutes → write `TODO` in your journal and move on · 20 minutes → ask an AI for a *hint* using the prompt in `01-fastapi-start-here.md`. Solutions to the code exercises are at the bottom (look only after 20 minutes of trying).

**Labs need:** Terminal (or VS Code's terminal), a browser (Chrome is easiest: DevTools = `Cmd+Option+I`), and an internet connection.

---

## The big picture (15 min)

When you open `https://example.com/page` in a browser, a lot of separate problems get solved, one by one. Each problem has its own solution. **That's the whole of networking.**

| The problem | The solution | Day 1 part |
|---|---|---|
| Which **machine** do I talk to? | **IP address** | Part 1 |
| Which **program** on that machine? | **Port** | Part 1 |
| I only know a **name**, not an IP | **DNS** | Part 2 |
| Data gets lost, duplicated, reordered | **TCP** (reliable delivery) | Part 3 |
| Anyone on the way can read or change it, and I can't tell if the server is real | **TLS** (the lock in HTTPS) | Part 4 |
| What do we actually *say* to each other? | **HTTP** (a plain-text conversation) | Day 2 |

**An analogy that fits everything:**
- **IP address** = the street address of a building
- **Port** = the apartment number inside that building
- **DNS** = the phone book: you look up a *name* and get an *address*
- **TCP** = registered post with delivery receipts: lost letters are re-sent, and letters arrive in order
- **TLS** = a sealed, tamper-proof envelope, plus an ID check on the person who opens the door
- **HTTP** = the language the two sides speak: "please send me page X" → "here it is"

**The picture to keep in your head:**
```
 YOUR MAC                                                          THE SERVER
 ┌────────┐  1. "Where is example.com?"   ┌─────────┐
 │Browser │ ────────────────────────────▶ │  DNS    │   (answer: 93.184.x.x)
 │        │ ◀──────────────────────────── │resolver │
 │        │                               └─────────┘
 │        │  2. TCP: open a connection to 93.184.x.x : 443
 │        │ ═════════════════════════════════════════════════▶ ┌────────────┐
 │        │  3. TLS: prove you're example.com, agree on keys   │ web server │
 │        │ ◀════════════════════════════════════════════════▶ │  (port 443)│
 │        │  4. HTTP (encrypted): "GET /page"                  │            │
 │        │ ═════════════════════════════════════════════════▶ │            │
 │        │  5. HTTP (encrypted): "200 OK" + the page          └────────────┘
 │        │ ◀═════════════════════════════════════════════════
 └────────┘
```
(The numbers `93.184.x.x` are just an illustration.)

**Today's goal:** by tonight you can draw this picture from memory and explain every arrow. Parts 1–5 teach one arrow each. Part 6 is where you prove it.

---

# Part 1 · Addresses: IP, ports, localhost (35 min)

### 1.1 IP addresses
Every device on a network gets an **IP address**: a number that says "which machine".
- **IPv4:** four numbers from 0 to 255, like `192.168.1.20`. That's 32 bits, about **4.3 billion** addresses, which isn't enough for every phone, laptop and server in the world.
- **IPv6:** the newer format, 128 bits, written in hex like `2606:2800:220:1:248:1893:25c8:1946`. Same idea, vastly more addresses. Both are in use side by side.

### 1.2 Public vs private addresses
Your Mac does **not** have a unique address on the whole internet. At home you have **two** kinds of address:
- A **private** address (only meaningful inside your home network), from these reserved ranges:
  - `10.0.0.0` – `10.255.255.255`
  - `172.16.0.0` – `172.31.255.255`
  - `192.168.0.0` – `192.168.255.255`
- A **public** address, belonging to your **router**. When your Mac talks to the internet, the router swaps your private address for its public one and keeps a table so replies find their way back. This is called **NAT** (network address translation).

Why you care: a server on a cloud machine has a **public IP**, which is why anyone can reach it. A program running on your laptop has only a private IP, which is why your friend can't reach it from outside your Wi-Fi.

### 1.3 `localhost`
`127.0.0.1` is a special address that always means **"this very computer"**. Traffic sent to it never leaves your Mac; it's called the **loopback** address. The name `localhost` is a built-in nickname for `127.0.0.1` (and `::1` in IPv6). When you run `fastapi dev` and open `http://localhost:8000`, you're talking to your own machine.

### 1.4 Ports
An IP address gets you to the **machine**. A **port** (a number from 0 to 65535) picks the **program** on it. One machine can run a website, a database, and an email server all at once, each listening on its own port.

| Port | What usually listens there |
|---|---|
| 22 | SSH (remote login) |
| 53 | DNS |
| **80** | **HTTP** (web, unencrypted) |
| **443** | **HTTPS** (web, encrypted) |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8000, 8080 | development web servers (FastAPI's default is 8000) |

Rules worth knowing:
- Only **one program** can **listen** on a given IP:port at a time. A second one fails with "Address already in use".
- When your browser connects to a server, **your side also uses a port**, a random high number (an *ephemeral* port). So a connection is really **(your IP, your port) ↔ (server IP, server port)**. That's how one server on port 443 can talk to thousands of clients at once.
- Ports below 1024 are "well-known" and usually need admin rights to listen on.

### 1.5 Listening on `127.0.0.1` vs `0.0.0.0`
When a server starts, it chooses **which network interfaces to listen on**:
- `127.0.0.1` → **only this machine** can reach it
- `0.0.0.0` → **every interface** (your Wi-Fi, your LAN…), so other devices can reach it

This is behind a classic bug: *"it works on my machine but my teammate can't open it."* (And later, when you put your app in a Docker container, it must listen on `0.0.0.0`, or nothing outside the container can reach it.)

### Lab 1: Look at your own addresses (10 min)
Open Terminal and run:
```bash
ipconfig getifaddr en0
```
- **Expect:** an address like `192.168.x.x` or `10.x.x.x`. That's your **private** IP on Wi-Fi.
- If it prints nothing, your Wi-Fi may be `en1`: try `ipconfig getifaddr en1`. Or run `ifconfig | grep "inet "` and look at every line.
```bash
curl https://ifconfig.me
echo
```
- **Expect:** a different, **public** address (it's your router's). If this fails, try `curl https://api.ipify.org`.
- **Notice:** two different addresses for the same Mac. Write both in `notes/networking.md` and one sentence on why they differ.
```bash
ping -c 3 127.0.0.1
```
- **Expect:** replies in well under 1 ms. That's the loopback: traffic that never leaves your Mac.
```bash
cat /etc/hosts
```
- **Expect:** a line mapping `127.0.0.1` to `localhost`. That's the "nickname" from 1.3, stored in a plain text file.

### Lab 2: Ports, "address in use", and who is listening (15 min)
In Terminal create a scratch folder and start a tiny web server that listens **only on your machine**:
```bash
cd ~/backend-journey/python-fundamentals      # adjust if your folder is elsewhere
mkdir -p scratch && cd scratch
uv run python -m http.server 8080 --bind 127.0.0.1
```
Leave it running. Open **a second Terminal tab** (`Cmd+T`) and run:
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080
```
- **Expect:** `200` (a directory listing page).
```bash
lsof -i :8080
```
- **Expect:** a table with `python` (or `Python`), a PID, and `(LISTEN)`. That's the program that owns port 8080.
- Now try your **LAN address** (use the number from Lab 1):
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://$(ipconfig getifaddr en0):8080
```
- **Expect:** `000` and a "connection refused"-style failure. The server only listens on `127.0.0.1`, so the LAN address doesn't reach it.
- **Break it on purpose:** go back to the first tab, press `Ctrl+C`, and start it on **all interfaces**:
```bash
uv run python -m http.server 8080 --bind 0.0.0.0
```
(If macOS asks "Do you want the application 'python' to accept incoming network connections?" click **Deny** or **Allow**; either works for this lab.) Run the same two `curl` commands again.
- **Expect:** `200` for **both** now.
- **Now start a second server on the same port.** In a third tab (still with the first running): `uv run python -m http.server 8080` from the `scratch` folder.
- **Expect:** `OSError: [Errno 48] Address already in use`. One program per port.
- Press `Ctrl+C` in every tab to stop the servers.
- **Write in your notes:** which command made the LAN address work, and why.

**Part 1 done when**
- [ ] You can explain IP vs port vs `localhost` and public vs private IP
- [ ] You saw "connection refused" and "address in use" yourself
- [ ] You can say what `127.0.0.1` vs `0.0.0.0` changes

---

# Part 2 · Names: DNS (35 min)

### 2.1 The problem
Humans remember `example.com`. Computers need `93.184.x.x`. **DNS (Domain Name System)** is the worldwide phone book that turns a **name** into an **address**. Servers also move, and one name can point at many machines, so the indirection is useful: change the DNS record and the same name now points at a new server.

### 2.2 Who actually answers?
Nobody has the whole phone book. DNS is a **hierarchy**, and a helper called a **recursive resolver** (run by your ISP, or Google `8.8.8.8`, or Cloudflare `1.1.1.1`) walks it for you:
```
Browser cache ─▶ Mac's cache ─▶ Recursive resolver (e.g. 8.8.8.8)
                                       │  (if it doesn't already have the answer cached)
                                       ├─▶ Root servers ("."): "ask the .com servers"
                                       ├─▶ .com servers:       "ask example.com's own name servers"
                                       └─▶ example.com's authoritative name servers: "the IP is 93.184.x.x"
```
The **authoritative** name servers are the ones that hold the real records for a domain. Everyone else just **caches** answers.

### 2.3 Records and TTL
A domain has **records**. The ones you'll meet:

| Type | Meaning | Example |
|---|---|---|
| **A** | name → IPv4 address | `example.com → 93.184.x.x` |
| **AAAA** | name → IPv6 address | |
| **CNAME** | name → another *name* (an alias) | `www.example.com → example.com` |
| **MX** | where this domain's email goes | |
| **TXT** | free text (domain ownership proofs, email security) | |
| **NS** | which servers are authoritative for this domain | |

Every answer carries a **TTL (time to live)**: how many seconds it may be cached. During that time, caches won't ask again.

**"DNS propagation takes 24–48 hours"** is a half-myth. What really happens: you change a record, but caches around the world keep serving the **old** answer until their TTL runs out. A low TTL means changes spread fast.

### 2.3 Why this matters for you
When you deploy a backend (Module 2 of your later plan), you'll **create an A record** that points your domain at your server's IP. HTTPS certificates are only issued if the domain really points at your server. So DNS is the first link in the chain.

### Lab 3: Read DNS answers with `dig` (20 min)
```bash
dig +short example.com
```
- **Expect:** one or two IP addresses.
```bash
dig example.com
```
- **Expect:** a long answer. Find these parts:
  - `;; ANSWER SECTION:` with a line like `example.com.  300  IN  A  93.184.x.x`. The columns are **NAME, TTL, CLASS, TYPE, DATA**
  - `;; Query time:` (how long the lookup took) and `;; SERVER:` (which resolver answered)
- **Run it again right away.** The TTL number usually **counts down** (e.g. `287` instead of `300`): you're reading a cached answer.
```bash
dig AAAA example.com +short
dig NS example.com +short
dig MX gmail.com +short
```
- **Notice:** the different record types.
```bash
dig @8.8.8.8 example.com +short
dig @1.1.1.1 example.com +short
```
- **Notice:** you asked two different resolvers directly. Usually they agree.
```bash
dig this-domain-does-not-exist-12345.com
```
- **Expect:** `status: NXDOMAIN` in the header. That's the "no such name" error, which browsers show as `DNS_PROBE_FINISHED_NXDOMAIN`.
```bash
dig +trace example.com
```
- **Expect:** a staircase of answers: first the **root** servers (`.`), then the **.com** servers, then the domain's own **authoritative** servers. This is the hierarchy from 2.2, visible.
- **Optional:** `dig www.wikipedia.org`. If you see a `CNAME` line before the `A` record, that's an alias chain.

### Lab 4: DNS from Python (5 min)
Create `python-fundamentals/drills/d1_dns.py`:
```python
import socket

print(socket.gethostbyname("example.com"))                        # one IPv4 address
for family, kind, proto, canon, sockaddr in socket.getaddrinfo("example.com", 443, type=socket.SOCK_STREAM):
    print(family.name, sockaddr)                                   # IPv4 and/or IPv6 results
```
Run it: `uv run python drills/d1_dns.py`
- **Notice:** your own program asked DNS with one function call. Every `requests`/`httpx` call does this first.

**Part 2 done when**
- [ ] You can explain what a resolver does and what an A record and TTL are
- [ ] You saw a TTL count down and an `NXDOMAIN`
- [ ] You can say why "I changed my DNS but still see the old site" happens

---

# Part 3 · The pipes: packets, TCP, UDP, latency (40 min)

### 3.1 Packets
Data doesn't travel as one big blob. It's cut into small **packets**, and each packet is sent and routed separately through many **routers** (each stop is a **hop**). Packets can be **lost**, arrive **out of order**, or arrive **twice**. The basic internet layer (IP) just does "best effort".

### 3.2 TCP: reliable delivery on top of unreliable packets
**TCP** turns that mess into a clean, reliable, ordered **stream of bytes**:
1. **Handshake** (one round trip) before any data:
   ```
   Client ── SYN ───────▶ Server      "I'd like to connect"
   Client ◀── SYN-ACK ─── Server      "OK, I'm ready"
   Client ── ACK ───────▶ Server      "Great. Starting now"
   ```
2. Data flows in numbered pieces. The receiver sends **acknowledgements**. If an ACK doesn't come, the sender **resends**.
3. TCP slows down if the network is congested and speeds up when it isn't.
4. At the end, both sides close the connection politely.

HTTP (the web) runs **on top of TCP**. So does PostgreSQL, SSH and email.

One detail that bites beginners: TCP is a **stream with no message boundaries**. If you send two messages, the other side might read them glued together, or one message in two pieces. Protocols on top (like HTTP) add their own rules ("the body is exactly Content-Length bytes") to cope.

### 3.3 UDP: fast, no promises
**UDP** has no handshake, no acknowledgements, no resending, no ordering. Each message is a standalone **datagram** that may or may not arrive. That sounds worse, but it's perfect when speed matters more than perfection: video calls, online games, **DNS lookups**, and **HTTP/3** (via a protocol called QUIC).

### 3.4 Latency vs bandwidth
- **Latency:** how long one trip takes. The round trip is the **RTT**. Typical orders of magnitude: same machine under 1 ms · same city a few ms · across a country tens of ms · across the world 100–250 ms.
- **Bandwidth:** how much data per second.

A **slow API call is usually about latency, not bandwidth.** Every step that needs a reply costs one RTT:
```
New HTTPS request to a server with a 50 ms round trip:
  DNS lookup ................................ ~ a few ms (often cached)
  TCP handshake ............................. 1 RTT  = 50 ms
  TLS handshake (TLS 1.3) ................... 1 RTT  = 50 ms
  The HTTP request and first byte back ...... 1 RTT  = 50 ms  (+ the time your server spends working)
                                              ≈ 150 ms+ before the first byte
```
This is why **reusing connections** ("keep-alive") matters, why chatty APIs (many small calls) feel slow, and why servers near users feel faster.

### Lab 5: Measure latency (15 min)
```bash
ping -c 4 example.com
```
- **Expect:** four replies with `time=… ms`, and a summary `min/avg/max`. (Some servers block ping. If you get no reply, try `ping -c 4 google.com`.)
- **Write down** the average. Compare with `ping -c 4 127.0.0.1` from Part 1.
```bash
traceroute -n example.com
```
- **Expect:** a numbered list, one line per **hop** (router) between you and the server, with times. Lines of `* * *` mean a router didn't answer; that's normal. It may take 10–20 seconds.
```bash
curl -o /dev/null -s -w "dns:        %{time_namelookup}s\nconnect:    %{time_connect}s\ntls:        %{time_appconnect}s\nfirst byte: %{time_starttransfer}s\ntotal:      %{time_total}s\n" https://example.com
```
- **Expect:** five numbers. **They are cumulative** (each includes the ones before it). Work out each phase by subtraction and write it in your notes:
  - DNS = `dns`
  - TCP handshake = `connect − dns`
  - TLS handshake = `tls − connect`
  - Waiting for the server = `first byte − tls`
  - Download = `total − first byte`
- **Run it 3 times.** Notice DNS getting close to 0 (cached).
- **Run it for plain HTTP:** the same command with `http://example.com`. **Expect:** `tls` is `0.000` because there's no TLS step. (It may also show a redirect; that's fine.)
```bash
nc -vz -G 3 example.com 443
nc -vz -G 3 example.com 81
```
- **Expect:** the first says `succeeded!` (something is listening on 443). The second times out or is refused (nothing listens on 81). `nc -vz` is "can I open a TCP connection to this port?", the quickest way to test whether a port is reachable.

### Lab 6: TCP and UDP with your own hands (15 min)
Create `python-fundamentals/drills/d1_sockets.py` and **type it** (don't paste). It runs a tiny TCP server and a UDP receiver on your own machine, so you can see both behaviours.
```python
import socket
import threading
import time

# ---------- TCP: connect, then talk ----------
ready = threading.Event()


def tcp_server() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 9998))      # listen on port 9998, this machine only
        srv.listen()
        ready.set()                        # tell the main thread: we're listening
        conn, addr = srv.accept()          # waits here until a client connects
        with conn:
            data = conn.recv(1024)
            conn.sendall(b"echo: " + data)


thread = threading.Thread(target=tcp_server)
thread.start()
ready.wait()

start = time.perf_counter()
with socket.create_connection(("127.0.0.1", 9998)) as client:      # the handshake happens here
    print("TCP connect took", round((time.perf_counter() - start) * 1000, 2), "ms")
    client.sendall(b"hello tcp")
    print(client.recv(1024))                                        # b'echo: hello tcp'
thread.join()

# ---------- UDP: no connection at all ----------
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver.bind(("127.0.0.1", 9999))
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender.sendto(b"hello udp", ("127.0.0.1", 9999))                    # just fire it off
data, addr = receiver.recvfrom(1024)
print(data, "from", addr[0])
receiver.close()
sender.close()
```
Run: `uv run python drills/d1_sockets.py`
- **Expect:** a TCP connect time of a few milliseconds, `b'echo: hello tcp'`, then `b'hello udp' from 127.0.0.1`.
- **Notice in the code:** TCP needs `listen` → `accept` → `create_connection` (a connection exists). UDP has just `sendto` and `recvfrom` (no connection).
- **The big realisation:** a web server is just a program that does `bind` → `listen` → `accept`, then reads text and writes text back. FastAPI and uvicorn are built on exactly this.

**Part 3 done when**
- [ ] You can describe the TCP handshake and what TCP adds on top of IP
- [ ] You can say when UDP is the better choice
- [ ] You measured the five `curl` timings and can explain each

---

# Part 4 · The lock: TLS and HTTPS (35 min)

### 4.1 The problem
Packets travel through many routers, Wi-Fi networks and cables you don't control. Without protection, someone on the path could:
1. **Read** your data (passwords, cookies),
2. **Change** it, or
3. **Pretend to be** the server.

### 4.2 What TLS gives you
**TLS (Transport Layer Security)** wraps a TCP connection and provides three things:
| Property | Meaning |
|---|---|
| **Confidentiality** | nobody on the path can read the data |
| **Integrity** | nobody can change it without being detected |
| **Authentication** | you're really talking to the real `example.com` |

**HTTPS = HTTP carried inside TLS**, normally on port **443**.

### 4.3 How it works (the idea, not the maths)
Two kinds of cryptography work together:
- **Asymmetric** (public/private key pairs): slow, but lets two strangers agree on a secret safely and lets a server *prove* who it is by signing something with its private key.
- **Symmetric** (one shared secret key): very fast, used to encrypt the actual data.

The handshake (TLS 1.3, **one round trip**):
```
Client ── "Hello. I want example.com. I support these ciphers" ─▶ Server
Client ◀── "Here's my certificate + my half of a key exchange" ── Server
        (the client checks the certificate)
Client ── "Here's my half of the key exchange" ─────────────────▶ Server
            both sides now compute the same secret key
Client ◀═══════ everything from here on is encrypted ═══════════▶ Server
```

### 4.4 Certificates and trust
A **certificate** is a document that says: *"the public key X belongs to the domain `example.com`, valid from date A to date B"*, **signed by a Certificate Authority (CA)**.

Why would your Mac believe the signature? Your operating system ships with a list of **trusted root CAs**. A server sends its certificate plus the **intermediate** certificates, forming a **chain**:
```
Root CA (already trusted by your Mac)
   └─ signs → Intermediate CA
                 └─ signs → the server's certificate for example.com
```
Your browser (or `curl`) checks that:
1. The chain leads to a **trusted root**
2. The certificate is for **this domain name** (the exact name you typed)
3. It hasn't **expired** (and isn't yet-to-be-valid)

If any check fails you get a scary warning or an error. **Let's Encrypt** is a free CA that issues certificates automatically (valid 90 days, renewed by software). Later you'll use **Caddy**, which gets and renews them for you.

### 4.5 What HTTPS does NOT do
- It doesn't hide **which IP and port** you connect to, and the **domain name** is usually visible during the handshake (and in DNS).
- It doesn't make a site **trustworthy**: a scam site can have a perfectly valid certificate. The lock means "private line to *that* domain", not "good website".
- It doesn't fix bugs in the **application** (SQL injection, weak passwords, broken permissions).

### Lab 7: Look at a real certificate (20 min)
```bash
curl -v https://example.com 2>&1 | head -40
```
- **Expect:** lines starting with `*` about the connection. Look for the **TLS version** (`TLSv1.3`), a **cipher** name, and (depending on your curl) lines with the certificate **subject**, **issuer**, **start date** and **expire date**. The exact wording differs between Macs.
```bash
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```
- **Expect:** four lines: `subject=` (the domain), `issuer=` (the CA), `notBefore=`, `notAfter=`.
```bash
openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null 2>/dev/null | grep -E " s:| i:"
```
- **Expect:** the **chain**: each certificate's subject (`s:`) and who issued it (`i:`). Notice how one certificate's issuer is the next one's subject.
- **In your browser:** open `https://example.com`.
  - **Chrome:** click the icon at the left of the address bar → "Connection is secure" → "Certificate is valid". Look at *Issued to*, *Issued by*, and the dates.
  - **Safari:** click the lock icon → "Show Details" → "Show Certificate".
- **See the trust list:** open **Keychain Access** (Spotlight: `Cmd+Space`, type it) → in the left bar choose **System Roots** → **Certificates**. Those are the roots your Mac trusts. Look for a name like "ISRG Root X1" (Let's Encrypt's root).
- **Make it fail on purpose** (these are public test sites made for this; if one is down, skip it):
```bash
curl -sS -o /dev/null https://expired.badssl.com/
curl -sS -o /dev/null https://wrong.host.badssl.com/
curl -sS -o /dev/null https://self-signed.badssl.com/
```
- **Expect:** three different errors: certificate **expired**, **hostname mismatch**, **self-signed** (not signed by a trusted CA). Match each error to the three checks in 4.4.
- **Plain text vs encrypted:** run `curl -v http://example.com 2>&1 | head -20`. Notice you can read the request lines in clear text. On a real network, anyone on the path could read that too, which is exactly what TLS prevents.

**Part 4 done when**
- [ ] You can name the three properties TLS provides
- [ ] You can explain what a certificate says and why your Mac trusts it
- [ ] You triggered the three certificate errors and know what each means
- [ ] You can say two things HTTPS does *not* protect

---

# Part 5 · The middlemen and the whole journey (20 min)

### 5.1 Who sits between the browser and your code
Between a user and your FastAPI app there are usually several helpers:

| Helper | What it does |
|---|---|
| **Reverse proxy** (Caddy, Nginx) | Sits **in front of your app**. Handles HTTPS (**"TLS termination"**), forwards requests to your app, can serve static files |
| **Load balancer** | Spreads incoming requests across **several copies** of your app (round-robin, least busy…) |
| **CDN** (Cloudflare…) | Keeps **cached copies** of files at servers near users |
| **Firewall** | Allows or blocks traffic by IP and port |
| **Forward proxy / VPN** | On the **client's** side: hides or routes the client's traffic |

A typical production setup for what you're about to build:
```
Browser ─▶ DNS ─▶ (CDN) ─▶ Reverse proxy ─▶ FastAPI app ─▶ PostgreSQL
                          (HTTPS ends here)   (port 8000)    (port 5432)
                          open to the internet                NOT open to the internet
```
**Security habit:** only ports **80 and 443** should be open to the world. The database port (5432) must never be reachable from the internet; only your app, on the private side, talks to it.

### 5.2 The complete journey, with what can go wrong
You type `https://example.com/page`:

| # | Step | What happens | If it fails, you see… | Tool to check |
|---|---|---|---|---|
| 1 | Parse | Browser splits the URL (scheme, host, port, path) | invalid URL | your eyes |
| 2 | DNS | name → IP | `DNS_PROBE_FINISHED_NXDOMAIN`, "server not found" | `dig` |
| 3 | TCP | connect to IP:443 | **Connection refused** (nothing listening), **timed out** (blocked/wrong IP/down) | `nc -vz`, `ping`, `traceroute` |
| 4 | TLS | certificate checked, keys agreed | expired / wrong host / untrusted certificate | `openssl s_client`, `curl -v` |
| 5 | HTTP request | `GET /page` sent | | Day 2 |
| 6 | Server work | proxy → app → database | **502/503/504** (proxy can't get an answer from your app) | your app's logs |
| 7 | HTTP response | status + headers + body | **404**, **500**… | Day 2 |
| 8 | Render | browser parses HTML, fires more requests (images, scripts, API calls) | slow or broken page | DevTools → Network |

**This table is your debugging map.** When something is broken, first ask *which step is failing*, then use that step's tool. Most "mystery" problems are one of steps 2, 3 or 4.

### Lab 8: See the whole journey in the browser (10 min)
- Open Chrome → `https://example.com` → DevTools (`Cmd+Option+I`) → **Network** tab → reload (`Cmd+R`).
- Click the **first** request → **Timing**. Find *DNS Lookup*, *Initial connection*, *SSL*, *Waiting for server response*, *Content Download*. These are steps 2, 3, 4, 6 and 7. Compare with your `curl` numbers from Lab 5.
- Notice how many **other** requests a real page makes (step 8). Each one may cost round trips.

**Part 5 done when**
- [ ] You can describe a reverse proxy, a load balancer and a CDN in one sentence each
- [ ] You can say which tool you'd use for a DNS failure, a refused connection and a certificate error

---

# Part 6 · Put it in your own words, code, quiz (35 min)

### 6.1 Teach-back (10 min)
Do these **without looking at this file**.
1. On paper, **redraw the big picture** from memory: boxes for Browser, DNS resolver and Server, and numbered arrows for DNS, TCP, TLS, HTTP request, HTTP response.
2. In `notes/networking.md`, write **"What happens when I type a URL"** in your own words (about 10 lines).
3. Add a table with 6 rows: **IP, port, DNS, TCP, TLS, reverse proxy**: what each is, in one sentence.
4. Then compare with the file and fix what you got wrong. The corrections are where the learning is.

### 6.2 Two code exercises (15 min)
Create `python-fundamentals/drills/d1_net_exercises.py`. Imports at the top: `import ipaddress` and `from urllib.parse import parse_qs, urlparse`. Paste the `raises` helper from your Python drills at the top as well:
```python
def raises(exc_type, fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except exc_type:
        return True
    return False
```
**Exercise 1.** `describe_url(url: str) -> dict`: split a URL into its parts, as a dict with the keys `scheme`, `host`, `port`, `path`, `query` (a dict of strings), `fragment`.
- If the URL has no port, use the default for its scheme (`http` → 80, `https` → 443)
- If the path is empty, use `"/"`
- *Hints:* `urlparse(url)` gives `.scheme`, `.hostname`, `.port`, `.path`, `.query`, `.fragment`; `parse_qs("x=1&y=2")` gives `{"x": ["1"], "y": ["2"]}` (lists), so take the first item of each.

**Exercise 2.** `classify_ip(ip: str) -> str`: return `"loopback"`, `"private"` or `"public"`. An invalid address must raise `ValueError`.
- *Hints:* `addr = ipaddress.ip_address(ip)`, then `addr.is_loopback` and `addr.is_private`. Check loopback **first**.

**Self-check** (paste at the bottom; the file should end with the `OK` line)
```python
assert describe_url("https://example.com/path/page?x=1&y=2#top") == {
    "scheme": "https", "host": "example.com", "port": 443,
    "path": "/path/page", "query": {"x": "1", "y": "2"}, "fragment": "top",
}
d = describe_url("http://localhost:8000/api/v1/projects?limit=20")
assert d["host"] == "localhost" and d["port"] == 8000 and d["query"] == {"limit": "20"}
d = describe_url("http://example.com")
assert d["port"] == 80 and d["path"] == "/" and d["query"] == {} and d["fragment"] == ""

assert classify_ip("127.0.0.1") == "loopback"
assert classify_ip("::1") == "loopback"
assert classify_ip("192.168.1.20") == "private"
assert classify_ip("10.0.0.5") == "private"
assert classify_ip("172.16.4.4") == "private"
assert classify_ip("172.32.0.1") == "public"
assert classify_ip("8.8.8.8") == "public"
assert raises(ValueError, classify_ip, "999.1.1.1")
print("D1 EXERCISES OK")
```
Run: `uv run python drills/d1_net_exercises.py`
- **Think about it:** `172.32.0.1` is *public* but `172.16.4.4` is private. Look back at the private ranges in 1.2 to see why.

### 6.3 The quiz (10 min)
Answer **in writing** in `notes/networking.md`, without looking. Then check against the answers at the bottom. Mark each ✓ or ✗; re-read the part for every ✗.

**Recall**
1. What does an IP address identify? What does a port identify?
2. Which three IP ranges are private? Which address means "this computer"?
3. What's the difference between listening on `127.0.0.1` and on `0.0.0.0`?
4. What does DNS do? Name four record types and what each is for.
5. What is a TTL, and what does it have to do with "DNS propagation"?
6. What does the TCP handshake accomplish, and how many round trips does it take?
7. TCP vs UDP: one sentence each, and one use of UDP.
8. Latency vs bandwidth: which usually makes an API call feel slow, and why?
9. What three properties does TLS provide?
10. What does a certificate claim, and who signs it? What three things does a client check?
11. Name two things HTTPS does **not** protect against.
12. What is TLS termination, and where does it usually happen?

**Scenarios** (which step of the journey is failing, and which tool would you use?)
13. Your teammate opens `http://<your-LAN-IP>:8000` and gets "connection refused", but it works for you on `localhost:8000`. Why?
14. You changed an A record an hour ago but some people still see the old site. Why?
15. A browser says `NET::ERR_CERT_DATE_INVALID`. Which step, and what's wrong?
16. `curl` says "Could not resolve host". Which step?
17. Starting your server says "Address already in use". What happened, and how do you find the culprit?
18. A user gets a **502 Bad Gateway** from your site. Which part of the chain has the problem?
19. Your page loads slowly even though the server answers in 10 ms. Name two causes related to today's topic.
20. Why must your database port never be open to the internet?

---

## Wrap-up (10 min)

1. **Cheat sheet:** add to `notes/00-python-cheatsheet.md` or `notes/networking.md`: the 6-row table from 6.1 and the **debugging map** from 5.2 (in your own words).
2. **Journal** (`journal.md`): `Did: … / Confused me: … / Tomorrow starts with: …`
3. **Commit and push** (VS Code Source Control: message, **Commit**, **Sync/Push**), or in Terminal:
   ```bash
   cd ~/backend-journey
   git add .
   git commit -m "day 1: networking A"
   git push
   ```

**Tomorrow (Day 2):** Networking B: **HTTP in depth** (requests, responses, methods, status codes, headers, cookies, REST). Tonight or tomorrow morning, tell me **"Day 2 please"** and anything that confused you today.

### Day 1 done when
- [ ] The big picture drawn from memory, and the "what happens when I type a URL" write-up done
- [ ] Labs 1–8 run (at least the ones with ✔ in your notes)
- [ ] `D1 EXERCISES OK` prints
- [ ] You answered the quiz and re-read the parts you missed
- [ ] Journal and commit done

---

# Quick reference (keep this)

| Term | One line |
|---|---|
| **IP address** | which machine (`192.168.1.20`) |
| **Private IP** | only valid inside a local network (`10.x`, `172.16–31.x`, `192.168.x`) |
| **Public IP** | reachable from the internet; your router's address at home |
| **NAT** | the router swapping private ↔ public addresses |
| **localhost / 127.0.0.1** | "this computer" (loopback) |
| **Port** | which program on the machine (0–65535) |
| **0.0.0.0 vs 127.0.0.1** | listen on all interfaces vs only this machine |
| **DNS** | name → IP, via a hierarchy and caches |
| **A / AAAA / CNAME / MX / TXT / NS** | IPv4 / IPv6 / alias / mail / text / name servers |
| **TTL** | how long an answer may be cached |
| **Packet / hop** | a small piece of data / one router on the path |
| **TCP** | reliable, ordered stream (handshake, ACKs, resend) |
| **UDP** | fast, no guarantees (DNS, video calls, HTTP/3) |
| **RTT / latency / bandwidth** | round-trip time / delay / data per second |
| **TLS / HTTPS** | encryption + integrity + identity; HTTP inside TLS (port 443) |
| **Certificate / CA** | "this key belongs to this domain", signed by a trusted authority |
| **Let's Encrypt** | free, automated CA (90-day certificates) |
| **Reverse proxy** | in front of your app; ends HTTPS, forwards requests |
| **Load balancer / CDN / firewall** | spreads load / caches near users / allows or blocks by IP and port |

**Mac commands from today:** `ipconfig getifaddr en0` · `ifconfig` · `ping -c 4 host` · `traceroute -n host` · `dig host` / `dig +short` / `dig +trace` · `lsof -i :PORT` · `nc -vz -G 3 host port` · `curl -v URL` · `curl -w …` · `openssl s_client -connect host:443 -servername host`

---

# Solutions to the code exercises (open only after 20 minutes of trying)

```python
import ipaddress
from urllib.parse import parse_qs, urlparse

DEFAULT_PORTS = {"http": 80, "https": 443}


def describe_url(url: str) -> dict:
    parts = urlparse(url)
    return {
        "scheme": parts.scheme,
        "host": parts.hostname,
        "port": parts.port or DEFAULT_PORTS[parts.scheme],
        "path": parts.path or "/",
        "query": {key: values[0] for key, values in parse_qs(parts.query).items()},
        "fragment": parts.fragment,
    }


def classify_ip(ip: str) -> str:
    addr = ipaddress.ip_address(ip)      # raises ValueError for an invalid address
    if addr.is_loopback:
        return "loopback"
    if addr.is_private:
        return "private"
    return "public"
```
`172.32.0.1` is public because the private block is only `172.16.0.0`–`172.31.255.255`.

---

# Quiz answers

1. An IP address identifies a **machine** on a network. A port identifies a **program** on that machine.
2. `10.0.0.0/8`, `172.16.0.0–172.31.255.255`, `192.168.0.0/16`. `127.0.0.1` (`localhost`) means this computer.
3. `127.0.0.1`: only this machine can connect. `0.0.0.0`: every network interface, so other devices can connect too.
4. DNS turns a **name into an IP address**. **A:** name → IPv4 · **AAAA:** name → IPv6 · **CNAME:** alias to another name · **MX:** where the domain's email goes · (also TXT: text/verification, NS: authoritative name servers).
5. A **TTL** is how many seconds an answer may be cached. "Propagation" delay is really old cached answers living until their TTL expires.
6. It sets up a connection (both sides agree they're ready and on sequence numbers) so data can be delivered reliably. It takes **one round trip** (SYN, SYN-ACK, ACK).
7. **TCP:** reliable, ordered delivery with a connection. **UDP:** fire-and-forget datagrams with no guarantees. UDP is used for DNS lookups, video calls, games, HTTP/3.
8. **Latency.** Every step that needs a reply costs a round trip; many small calls add up, while bandwidth is rarely the limit for API calls.
9. **Confidentiality** (nobody can read it), **integrity** (nobody can change it unnoticed), **authentication** (you're talking to the real server).
10. A certificate claims "this public key belongs to this domain, valid from A to B", and it's signed by a **Certificate Authority**. The client checks: the chain leads to a **trusted root**, the certificate matches the **domain name**, and it's **within its validity dates**.
11. Any two of: which IP/port you connect to, (often) the domain name, whether the site is trustworthy, bugs in the application (SQL injection, weak passwords, broken permissions).
12. **TLS termination** means the HTTPS encryption is ended (decrypted) at a **reverse proxy or load balancer** in front of your app, which then forwards plain requests to the app on a private side.
13. Your server is listening on `127.0.0.1` only. It must listen on `0.0.0.0` (and the LAN firewall must allow it) to be reachable from other devices. *(Step 3, TCP; check with `lsof -i :8000` and `nc -vz`.)*
14. Caches still hold the **old** answer until its **TTL** expires. *(Step 2, DNS; compare `dig @8.8.8.8` with your local answer.)*
15. **Step 4, TLS.** The certificate's validity dates are wrong: it has **expired** (or isn't valid yet). Check with `openssl s_client … | openssl x509 -noout -dates`.
16. **Step 2, DNS.** The name can't be resolved. Check with `dig`.
17. Another program already listens on that port. Find it with `lsof -i :PORT`, then stop it or use a different port.
18. The **reverse proxy/load balancer** couldn't get a valid answer from your **app** (crashed, not started, wrong port, too slow). Look at your app's logs and check that it's listening.
19. Many round trips: **new connections each time** (no keep-alive: TCP + TLS handshakes repeated), **many separate requests** (chatty API or lots of assets), a **far-away server** (high latency), or slow **DNS**.
20. Anyone on the internet could try to connect and attack or read it. Only your app (on the private side of the network) should be able to reach the database; the internet should only reach ports 80/443.

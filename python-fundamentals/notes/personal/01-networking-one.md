# 01 · Networking One · Personal Notes

> 🧭 **Fast revision format:** Technical detail is preserved, but each section is visually separated. Read the bold lines and callouts first; then expand only where you feel uncertain.

## 📚 Table of contents

- [60-second picture](#60-second-picture)
- [1. Address, machine, and program](#1-address-machine-and-program)
  - [Private, public, and NAT](#private-public-and-nat)
  - [Localhost and loopback](#localhost-and-loopback)
  - [Ports](#ports)
  - [Binding and network interfaces](#binding-and-network-interfaces)
- [2. DNS: name to IP](#2-dns-name-to-ip)
- [3. Packets, TCP, UDP, and latency](#3-packets-tcp-udp-and-latency)
- [4. TLS and HTTPS](#4-tls-and-https)
- [5. Complete journey and debugging map](#5-complete-journey-and-debugging-map)
- [Most common confusions](#most-common-confusions)
- [One-sentence recall table](#one-sentence-recall-table)
- [Fast recall drill](#fast-recall-drill)

### Visual guide

| Mark | Meaning |
|---|---|
| 🧠 **Remember** | High-value recall point |
| ❓ **Doubt resolved** | A clarification that previously caused confusion |
| ⚠️ **Trap** | Easy mistake or misleading wording |
| 🔁 **Recall** | Connection with another networking concept |
| 🛠️ **Practical** | Command, debugging step, or implementation detail |

## 60-second picture

When you open `https://example.com/page`:

1. **DNS** finds the server IP.
2. **TCP** opens a reliable connection to `IP:443`.
3. **TLS** verifies the server and creates encryption keys.
4. **HTTP** sends `GET /page` through that secure connection.
5. The server sends a response, and the browser renders it.

**Memory sentence:**  
**Name → address → connection → secure connection → conversation.**

```text
Browser → DNS → IP:443 → TCP → TLS → HTTP request/response
```

---

# Day 1: A request's journey

## 1. Address, machine, and program

| Term | What it means | Analogy |
|---|---|---|
| **IP address** | Identifies a machine/network interface | Building address |
| **Port** | Identifies a program on that machine | Apartment number |
| **IP:port** | Exact endpoint you connect to | Building + apartment |

**IPv4:** `192.168.1.20` — 32-bit, four numbers.  
**IPv6:** `2606:2800:220:1:248:1893:25c8:1946` — 128-bit, hex format.

### Private, public, and NAT

- **Private IP:** used inside a local network.
  - `10.0.0.0`–`10.255.255.255`
  - `172.16.0.0`–`172.31.255.255`
  - `192.168.0.0`–`192.168.255.255`
- **Public IP:** globally routable internet address; normally belongs to the router or cloud server.
- **NAT:** the router replaces private IP/port details with public IP/port details and tracks replies.

> Private IP reuse is normal across separate networks. Public IPs are generally globally unique; Carrier-Grade NAT (CGNAT) is an ISP-level exception where customers share public IPv4 addresses.

**Who assigns what?**

- **Router/DHCP:** assigns private IPs inside a local network.
- **ISP:** usually assigns the router its public IP, which may be dynamically reused or shared.
- **Cloud provider/DHCP:** assigns addresses to cloud machines.
- You can manually configure a private IP, but DHCP is the normal method.

### Localhost and loopback

- `127.0.0.1` = this Mac, IPv4 loopback
- `::1` = this Mac, IPv6 loopback
- `localhost` = built-in name for loopback
- Loopback traffic stays inside the machine; Wi-Fi and the internet are not involved.

**Useful mental model:**

- `127.0.0.1:8000` → another program inside this same Mac
- `192.168.1.x:8000` → this Mac as seen by another device on the LAN
- `203.0.113.10:443` → a public internet server

### Ports

Common ports:

| Port | Service |
|---|---|
| 22 | SSH |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8000/8080 | development web servers |

- Ports select programs, not machines.
- Only one program may listen on the same IP and port.
- Your browser also uses a random **ephemeral** port, so a connection is `(client IP, client port) ↔ (server IP, 443)`.
- Ports below 1024 are usually privileged.

### Binding and network interfaces

A **network interface** is a connection point for network traffic:

- Wi-Fi: own IP
- Ethernet: own IP
- VPN: virtual interface/IP
- Loopback: `127.0.0.1` or `::1`

| Binding | Meaning |
|---|---|
| `127.0.0.1` | Listen for IPv4 connections from this machine only |
| `::1` | Listen for IPv6 connections from this machine only |
| `0.0.0.0` | Listen on every IPv4 interface |
| `::` | Listen on every IPv6 interface |

Binding to `0.0.0.0` does not itself bypass firewalls or guarantee reachability. Binding to `127.0.0.1` will make a server unavailable to other devices.

**Fast remember rule:**

- `127.0.0.1` → works on this Mac
- `0.0.0.0` → potentially reachable through LAN IPs
- `::` / `::1` → IPv6 equivalents; dual-stack support is OS/configuration dependent

### Doubts resolved

- **Does `localhost` need Wi-Fi?** No. Loopback stays entirely on the machine.
- **Can private IP `192.168.1.10` exist in many homes?** Yes. It is reused across separate private networks.
- **Why did `localhost:8000` work but my LAN IP did not?** The server was probably bound to `127.0.0.1`, not `0.0.0.0`.
- **Does `0.0.0.0` accept IPv6?** No. Use `::` for IPv6. An IPv6 wildcard socket may sometimes support IPv4 too through dual-stack behavior, but do not rely on that.

---

## 2. DNS: name to IP

DNS solves: **“I know a name, but I need an address.”**

Example:

```text
google.com → 142.250.x.x
```

### Lookup path

1. **Browser cache**
2. **Operating-system cache**
3. **Recursive resolver** — finds the answer on behalf of the device
4. **Root DNS servers** — direct the resolver to the correct TLD
5. **TLD servers**, such as `.com` — direct the resolver to the domain's authoritative name servers
6. **Authoritative name servers** — hold the domain's actual DNS records
7. Resolver returns the answer and caches it

**No single server has every DNS record.** DNS is distributed between root, TLD, and domain-authoritative servers.

### DNS records

| Record | Purpose | Remembers |
|---|---|---|
| **A** | Domain → IPv4 address | A = IPv4 |
| **AAAA** | Domain → IPv6 address | Four A's = IPv6 |
| **MX** | Mail server for the domain | MX = mail exchange |
| **CNAME** | Alias to another domain name | CNAME = canonical name |
| **TXT** | Text/verification data | TXT = text |
| **NS** | Authoritative name servers | NS = name server |

For a CNAME: `www.example.com` follows to `example.com`, then to an A or AAAA record. A CNAME generally cannot coexist with other record types at the same DNS name.

### TTL and old DNS

**TTL = Time To Live.** It tells caches how long they may reuse a record.

Example:

```text
example.com  A  192.0.2.10  TTL 3600 seconds
```

The answer may be reused for up to one hour.

**Why do I still see the old website?**

- Browser cache
- Operating-system cache
- Recursive-resolver cache
- CDN cache
- Deployment/incomplete server update
- Different resolvers with different cache states

Lowering a TTL **after** a change does not immediately clear old cached answers. Those answers keep their previous expiry time.

> “DNS propagation” is mostly cache expiry, not a change travelling to every DNS server at the exact same moment.

### DNS cache flow

```text
Browser cache → OS cache → recursive resolver cache
→ root → TLD → authoritative server
→ resolver → browser
```

---

## 3. Packets, TCP, UDP, and latency

### Packets

Data is split into packets. Packets may:

- arrive out of order
- be lost
- arrive twice
- take different routes

IP does best-effort delivery. TCP adds reliability.

### TCP

**TCP = reliable, ordered byte stream.**

The three-way handshake is **one RTT**:

```text
Client → SYN        “I want to connect”
Client ← SYN-ACK    “I received that; I’m ready”
Client → ACK        “Agreed”
```

After connecting, TCP:

- numbers transmitted bytes
- acknowledges received bytes
- resends missing bytes
- reorders data
- controls congestion

**Important:** TCP preserves byte order, but it does **not** preserve message boundaries.

Sending:

```text
send("Hello")
send("World")
```

Receiving may read:

```text
HelloWorld
Hel
loWorld
HelloW
orld
```

Every outcome is ordered and valid.

**Therefore:** application protocols must define framing:

- HTTP: headers, `Content-Length`, or chunked transfer encoding
- Redis: RESP framing
- PostgreSQL: its wire protocol
- Custom TCP programs: implement a length prefix or delimiter

**Doubt resolved:** `recv(1024)` means “give me up to 1024 bytes now,” not “give me exactly one message.”

### UDP

**UDP = standalone datagrams, no handshake, no delivery guarantee, no ordering guarantee.**

Use when speed matters more than perfect delivery:

- DNS
- video calls
- online games
- HTTP/3 through QUIC

| | TCP | UDP |
|---|---|---|
| Guarantee | Ordered, reliable byte delivery | None |
| Message boundaries | No | Each datagram is separate |
| Setup | Handshake | No handshake |
| Typical use | HTTP, SSH, databases, email | DNS, voice/video, games |

### Latency vs bandwidth

- **Latency:** time for one operation/round trip
- **RTT:** round trip from client to server and back
- **Bandwidth:** amount of data that can move per second

**Slow API calls are often latency problems, not bandwidth problems.** A new HTTPS connection can cost:

```text
DNS       few ms or longer when uncached
TCP       1 RTT
TLS 1.3   1 RTT
HTTP      1 RTT plus server processing
```

For RTT = 50 ms and 5 ms DNS/10 ms processing:

```text
5 + 50 + 50 + 50 + 10 = 165 ms approximately
```

**Connection reuse/keep-alive** avoids repeating TCP and TLS handshakes. Chatty APIs and distant servers add RTTs.

---

## 4. TLS and HTTPS

### HTTPS timeline

For `https://api.example.com/users`:

1. **DNS:** resolve hostname to IP
2. **TCP:** establish reliable connection
3. **TLS:** authenticate the server and agree on shared encryption
4. **HTTP:** send the encrypted request
5. **Response:** server processes and returns it through TLS/TCP

### What TLS provides

| Property | Meaning |
|---|---|
| **Confidentiality** | Observers cannot read the data |
| **Integrity** | Undetected in-transit modification is prevented |
| **Authentication** | The client verifies that it is talking to the claimed domain |

**HTTPS = HTTP carried inside TLS, normally on port 443.**

### TLS 1.3 handshake

Simplified:

1. ClientHello: supported versions/ciphers + key-exchange information
2. ServerHello: selected parameters + key-exchange information
3. Server certificate: browser verifies identity
4. Both sides derive shared session keys
5. Application data becomes encrypted

TLS 1.3 normally uses **1 RTT**. TLS 1.2 commonly needed 2 RTTs for the full handshake.

The public/private key system and symmetric key system work together:

- **Asymmetric cryptography:** identity/key agreement
- **Symmetric cryptography:** fast encryption of the actual HTTP data

### Certificate and trust

A certificate says approximately:

> Public key X belongs to `example.com`, for this validity period, and it is signed by a Certificate Authority.

Trust chain:

```text
Mac trust store
  → trusted root CA
    → intermediate CA
      → example.com certificate
```

The client checks:

1. Chain leads to a trusted root
2. Certificate hostname matches the hostname requested
3. Certificate is currently valid and has not expired

**Authentication correction:** DNS tells the browser which IP to connect to. TLS then helps verify who owns the endpoint's certificate. TLS authentication does not prove that DNS was mapped correctly in every possible hostile environment.

### HTTPS does not protect against everything

HTTPS does **not** guarantee:

- the website is honest or safe
- the domain operator has good intentions
- SQL injection is prevented
- passwords are strong
- authorization is correct
- application code is secure

It also does not hide every network detail. An observer may infer:

- destination IP
- port 443
- data timing and size
- domain/name through DNS or TLS metadata, depending on protocol settings

But the HTTP request body, cookies, and response content are encrypted in transit.

### Example of the separation

If `GET /users/102/profile` returns user 102's profile to user 101:

- HTTPS worked
- TLS worked
- The server applied no authorization check

This is **broken access control**, an application-security problem—not a TLS failure.

---

## 5. Complete journey and debugging map

When a connection fails, identify the failed layer:

| Step | Failure | What to notice/check |
|---|---|---|
| Parse URL | Invalid URL | scheme, host, port, path |
| DNS | name cannot resolve | browser/OS cache, resolver, `dig` |
| TCP | refused or timed out | server listening, firewall, IP/port, `nc -vz`, `lsof` |
| TLS | certificate or handshake error | expiry, hostname, trusted chain, `curl -v`, `openssl s_client` |
| HTTP | 404/500 etc. | route/status/body in application logs |
| Proxy/app | 502/503/504 | reverse proxy cannot reach app |
| App/data | slow or error | app, database, external API |

### Middlemen

- **Reverse proxy:** receives public traffic, handles TLS termination, forwards requests to app
- **Load balancer:** distributes requests across app instances
- **CDN:** caches content closer to users
- **Firewall:** allows/blocks traffic by IP/port
- **Forward proxy/VPN:** routes traffic on the client side

A typical production shape:

```text
Browser → DNS → CDN → reverse proxy/load balancer
        → FastAPI app → PostgreSQL

Internet opens: 80 and 443
Database: private only, usually 5432 not public
```

**502/503/504:** usually the reverse proxy exists, but it could not get a valid/fast response from the application.

---

## Most common confusions

- **IP identifies machine; port identifies program.**
- **Private IP is not unique worldwide.**
- **TCP guarantees ordered bytes, not read-call boundaries.**
- **DNS cache/TTL explains old websites, not literal 24–48-hour mandatory propagation.**
- **TLS verifies the domain identity, not whether the business or application is safe.**
- **HTTPS does not fix SQL injection or authorization bugs.**
- **A new HTTPS connection pays TCP + TLS + HTTP round trips.**
- **0.0.0.0 listens on all IPv4 interfaces.**
- **127.0.0.1 listens only on loopback.**
- **Only one program should listen on an IP:port.**
- **Database ports should not be open to the internet.**

---

## One-sentence recall table

| Concept | Recall sentence |
|---|---|
| IP | Finds the machine/network interface |
| Port | Finds the program on that machine |
| NAT | Lets private LAN addresses share a public address |
| Localhost | Means this computer |
| DNS | Finds IPs for names |
| TTL | Sets the cache lifetime |
| TCP | Reliably delivers an ordered stream of bytes |
| UDP | Sends separate datagrams without guarantees |
| RTT | One client→server→client round trip |
| TLS | Encrypts, protects integrity, and authenticates the server |
| HTTPS | HTTP inside a TLS connection |
| Reverse proxy | Terminates public HTTPS and forwards to the app |

---

## Fast recall drill

Close this file and answer aloud:

1. Name the sequence: DNS, TCP, TLS, HTTP.
2. Explain IP vs port.
3. Explain `127.0.0.1` vs `0.0.0.0`.
4. Name A, AAAA, MX, CNAME.
5. Explain why TCP is a byte stream.
6. Explain latency vs bandwidth.
7. Name TLS's three properties.
8. Name two things HTTPS does not protect.
9. Which tool for DNS? For TCP reachability? For certificate details?
10. What is TLS termination?

**If you miss one, reread only that numbered section.**

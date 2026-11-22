import socket

print(socket.gethostbyname("example.com"))                        # one IPv4 address
for family, kind, proto, canon, sockaddr in socket.getaddrinfo("example.com", 443, type=socket.SOCK_STREAM):
    print(family.name, sockaddr)                                   # IPv4 and/or IPv6 results
import socket


if __name__ == '__main__':
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(hostname, ip_address)

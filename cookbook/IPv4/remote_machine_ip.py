import socket


if __name__ == '__main__':
    remote_host = 'www.python.org'
    print(remote_host, socket.gethostbyname(remote_host))

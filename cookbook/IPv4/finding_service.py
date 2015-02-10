import socket


if __name__ == '__main__':
    protocol = 'tcp'
    for port in (80, 25):
        service = socket.getservbyport(port)
        print('Port:', port)
        print('Service:', service)

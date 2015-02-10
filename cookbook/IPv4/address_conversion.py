from binascii import hexlify
import socket


if __name__ == '__main__':
    for ip in ['127.0.0.1', '192.168.0.1']:
        packed_ip = socket.inet_aton(ip)
        unpacked_ip = socket.inet_ntoa(packed_ip)
        print('Packed:', hexlify(packed_ip))
        print('Unpacked:', unpacked_ip)

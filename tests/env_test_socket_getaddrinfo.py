# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    from eventlet.green import socket
    print(socket.gethostbyname('localhost'))
    print(socket.getaddrinfo('localhost', 80))

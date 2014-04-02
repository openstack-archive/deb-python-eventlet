# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    from eventlet import patcher
    patcher.monkey_patch()
    import socket
    import urllib
    print("child {0} {1}".format(socket.socket, urllib.socket.socket))

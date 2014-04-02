from __future__ import print_function
# no standard tests in this file, ignore
__test__ = False


def parent(pid):
    import signal

    eventlet.Timeout(1)
    try:
        port = None
        while True:
            try:
                contents = open(signal_path, 'rb').read()
                port = int(contents.split()[0])
                break
            except (IOError, IndexError, ValueError, TypeError):
                eventlet.sleep(0.1)
        eventlet.connect(('127.0.0.1', port))
        while True:
            try:
                contents = open(signal_path, 'rb').read()
                result = contents.split()[1]
                break
            except (IOError, IndexError):
                eventlet.sleep(0.1)
        print('result {0}'.format(result.decode()))
    finally:
        os.kill(pid, signal.SIGTERM)


def child():
    sock = eventlet.listen(('', 0))
    with open(signal_path, 'wb') as fd:
        msg = '{0}\n'.format(sock.getsockname()[1]).encode()
        fd.write(msg)
        fd.flush()
        sock.accept()
        fd.write(b'done')

if __name__ == '__main__':
    import eventlet
    import os

    signal_path = os.path.join(os.environ['TMP'], 'fork_test_simple_signal.txt')
    pid = os.fork()
    if pid > 0:
        parent(pid)
    elif pid == 0:
        child()
    else:
        print('fork failed')

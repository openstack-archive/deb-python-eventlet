# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    from eventlet import patcher

    base = patcher.import_patched('patcher_test_base')
    print("defaults {0} {1} {2}".format(base, base.socket, base.urllib.socket.socket))

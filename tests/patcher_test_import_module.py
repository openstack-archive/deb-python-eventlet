# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import patcher_test_patching
    import socket

    patcher_test_patching.prepare()
    print("importing {0} {1} {2} {3}".format(
        patcher_test_patching,
        socket,
        patcher_test_patching.socket,
        patcher_test_patching.urllib,
    ))

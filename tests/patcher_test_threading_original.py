# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    from eventlet import patcher
    import threading
    _threading = patcher.original('threading')

    def test():
        print(repr(threading.currentThread()))

    t = _threading.Thread(target=test)
    t.start()
    t.join()
    print(len(threading._active))
    print(len(_threading._active))

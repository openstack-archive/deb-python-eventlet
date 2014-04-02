# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    from eventlet import tpool
    import threading

    def test():
        print(repr(threading.currentThread()))

    tpool.execute(test)
    print(len(threading._active))

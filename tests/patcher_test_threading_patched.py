# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    import threading

    def test():
        print(repr(threading.currentThread()))

    t = threading.Thread(target=test)
    t.start()
    t.join()
    print(len(threading._active))

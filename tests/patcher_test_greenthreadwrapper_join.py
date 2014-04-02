# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    import threading

    t2 = None

    def test():
        def test2():
            global t2
            t2 = threading.currentThread()
        eventlet.spawn(test2)

    t = eventlet.spawn(test)
    t.wait()

    print(repr(t2))
    t2.join()

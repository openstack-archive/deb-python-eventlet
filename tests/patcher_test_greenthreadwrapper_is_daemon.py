# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    import threading

    def test():
        t = threading.currentThread()
        print(t.is_daemon())
        print(t.isDaemon())

    t = eventlet.spawn(test)
    t.wait()

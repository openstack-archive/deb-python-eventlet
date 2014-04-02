# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    from eventlet import event
    import threading
    evt = event.Event()

    def test():
        print(repr(threading.currentThread()))
        evt.send()

    eventlet.spawn_n(test)
    evt.wait()
    print(len(threading._active))

# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    import threading

    def test():
        t = threading.currentThread()
        print(t.name)
        print(t.getName())
        print(t.get_name())
        t.name = 'foo'
        print(t.name)
        print(t.getName())
        print(t.get_name())
        t.setName('bar')
        print(t.name)
        print(t.getName())
        print(t.get_name())

    t = eventlet.spawn(test)
    t.wait()

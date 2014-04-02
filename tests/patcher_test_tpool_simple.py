# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import eventlet
    from eventlet import patcher
    patcher.monkey_patch()
    from eventlet import tpool
    print("child {0}".format(tpool.execute(len, "hi")))
    print("child {0}".format(tpool.execute(len, "hi2")))
    tpool.killall()

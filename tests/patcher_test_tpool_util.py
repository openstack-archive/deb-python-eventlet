# no standard tests in this file, ignore
__test__ = False


def check_tpool_patched():
    import time

    import eventlet
    from eventlet import tpool
    from eventlet.support import six

    tickcount = [0]

    def tick():
        for i in six.moves.range(1000):
            tickcount[0] += 1
            eventlet.sleep()

    def do_sleep():
        tpool.execute(time.sleep, 0.5)

    eventlet.spawn(tick)
    w1 = eventlet.spawn(do_sleep)
    w1.wait()
    print(tickcount[0])
    assert tickcount[0] > 900
    tpool.killall()

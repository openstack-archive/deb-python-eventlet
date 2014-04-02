from __future__ import print_function
# no standard tests in this file, ignore
__test__ = False


def fetch(dsn, num, secs):
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    for i in range(num):
        cur.execute("select pg_sleep(%s)", [secs])


def tick(count, totalseconds, persecond):
    for i in range(totalseconds * persecond):
        count[0] += 1
        eventlet.sleep(1.0 / persecond)


if __name__ == '__main__':
    import os
    import sys
    import eventlet
    eventlet.monkey_patch()
    from eventlet import patcher
    if not patcher.is_monkey_patched('psycopg'):
        print("Psycopg not monkeypatched")
        sys.exit(0)

    dsn = os.environ['PSYCOPG_TEST_DSN']
    import psycopg2

    count = [0]
    f = eventlet.spawn(fetch, dsn, 2, 1)
    t = eventlet.spawn(tick, count, 2, 100)
    f.wait()
    assert count[0] > 100, count[0]
    print("done")

# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    from eventlet import tpool
    import eventlet
    import os
    import threading
    import time

    limit = int(os.environ.get('eventlet_test_limit', '1'))
    thread_ids = set()

    def count():
        tid = threading.current_thread().ident
        thread_ids.add(tid)
        time.sleep(0.1)

    p = eventlet.GreenPool()
    for i in range(limit):
        p.spawn(tpool.execute, count)
    p.waitall()
    print(len(thread_ids))

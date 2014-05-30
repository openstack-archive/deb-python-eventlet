# import eventlet
# from eventlet import greenthread
# from eventlet.support import greenlets as greenlet
from tests import LimitedTestCase


_g_results = []


def passthru(*args, **kw):
    _g_results.append((args, kw))
    return args, kw


def waiter(a):
    greenthread.sleep(0.1)
    return a


def assert_dead(gt):
    if hasattr(gt, 'wait'):
        try:
            gt.wait()
            assert False, u'Expected GreenletExit exception'
        except greenlet.GreenletExit:
            pass
    assert gt.dead
    assert not gt


class TestSpawn(LimitedTestCase):
    def tearDown(self):
        global _g_results
        super(TestSpawn, self).tearDown()
        _g_results = []

    def test_simple(self):
        gt = greenthread.spawn(passthru, 1, b=2)
        self.assertEqual(gt.wait(), ((1,), {'b': 2}))
        self.assertEqual(_g_results, [((1,), {'b': 2})])

    def test_n(self):
        gt = greenthread.spawn_n(passthru, 2, b=3)
        self.assert_(not gt.dead)
        greenthread.sleep(0)
        self.assert_(gt.dead)
        self.assertEqual(_g_results, [((2,), {'b': 3})])

    def test_kill(self):
        gt = greenthread.spawn(passthru, 6)
        greenthread.kill(gt)
        assert_dead(gt)
        greenthread.sleep(0.001)
        self.assertEqual(_g_results, [])
        greenthread.kill(gt)
        assert_dead(gt)

    def test_kill_meth(self):
        gt = greenthread.spawn(passthru, 6)
        gt.kill()
        assert_dead(gt)
        greenthread.sleep(0.001)
        self.assertEqual(_g_results, [])
        gt.kill()
        assert_dead(gt)

    def test_kill_n(self):
        gt = greenthread.spawn_n(passthru, 7)
        greenthread.kill(gt)
        assert_dead(gt)
        greenthread.sleep(0.001)
        self.assertEqual(_g_results, [])
        greenthread.kill(gt)
        assert_dead(gt)

    def test_link(self):
        results = []

        def link_func(g, *a, **kw):
            results.append(g)
            results.append(a)
            results.append(kw)

        gt = greenthread.spawn(passthru, 5)
        gt.link(link_func, 4, b=5)
        self.assertEqual(gt.wait(), ((5,), {}))
        self.assertEqual(results, [gt, (4,), {'b': 5}])

    def test_link_after_exited(self):
        results = []

        def link_func(g, *a, **kw):
            results.append(g)
            results.append(a)
            results.append(kw)

        gt = greenthread.spawn(passthru, 5)
        self.assertEqual(gt.wait(), ((5,), {}))
        gt.link(link_func, 4, b=5)
        self.assertEqual(results, [gt, (4,), {'b': 5}])

    def test_link_relinks(self):
        # test that linking in a linked func doesn't cause infinite recursion.
        called = []

        def link_func(g):
            g.link(link_func_pass)

        def link_func_pass(g):
            called.append(True)

        gt = greenthread.spawn(passthru)
        gt.link(link_func)
        gt.wait()
        self.assertEqual(called, [True])


class TestSpawnAfter(TestSpawn):
    def test_basic(self):
        gt = greenthread.spawn_after(0.1, passthru, 20)
        self.assertEqual(gt.wait(), ((20,), {}))

    def test_cancel(self):
        gt = greenthread.spawn_after(0.1, passthru, 21)
        gt.cancel()
        assert_dead(gt)

    def test_cancel_already_started(self):
        gt = greenthread.spawn_after(0, waiter, 22)
        greenthread.sleep(0)
        gt.cancel()
        self.assertEqual(gt.wait(), 22)

    def test_kill_already_started(self):
        gt = greenthread.spawn_after(0, waiter, 22)
        greenthread.sleep(0)
        gt.kill()
        assert_dead(gt)


class TestSpawnAfterLocal(LimitedTestCase):
    def setUp(self):
        super(TestSpawnAfterLocal, self).setUp()
        self.lst = [1]

    def test_timer_fired(self):
        def func():
            greenthread.spawn_after_local(0.1, self.lst.pop)
            greenthread.sleep(0.2)

        greenthread.spawn(func)
        assert self.lst == [1], self.lst
        greenthread.sleep(0.3)
        assert self.lst == [], self.lst

    def test_timer_cancelled_upon_greenlet_exit(self):
        def func():
            greenthread.spawn_after_local(0.1, self.lst.pop)

        greenthread.spawn(func)
        assert self.lst == [1], self.lst
        greenthread.sleep(0.2)
        assert self.lst == [1], self.lst

    def test_spawn_is_not_cancelled(self):
        def func():
            greenthread.spawn(self.lst.pop)
            # exiting immediatelly, but self.lst.pop must be called
        greenthread.spawn(func)
        greenthread.sleep(0.1)
        assert self.lst == [], self.lst


import tempfile
import os
import thread, threading, time
# from eventlet.green import thread, threading, time


class FileCheckerThread(threading.Thread):
    """ Interrupt main-thread as soon as a changed module file is detected,
        the lockfile gets deleted or gets to old. """

    def __init__(self, interval, main_thread):
        threading.Thread.__init__(self)
        self.interval = interval
        self.main_thread = main_thread
        #: Is one of 'reload', 'error' or 'exit'
        self.status = None

    def run(self):
        print('FileCheckerThread loop 1')
        time.sleep(self.interval)
        print('FileCheckerThread loop 2')
        self.status = 'reload'
        thread.interrupt_main()
        # self.main_thread._Thread__stop()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, *_):
        if not self.status:
            self.status = 'exit'  # silent exit
        self.join()
        return exc_type is not None and issubclass(exc_type, KeyboardInterrupt)


class TestJoin(LimitedTestCase):
    TEST_TIMEOUT = 1000

    def test_join(self):
        main_thread = threading.current_thread()

        def server():
            time.sleep(0.5)

        with FileCheckerThread(self.lockfile, 0.1, main_thread):
            t = threading.Thread(run=server)
            t.start()
            t.join()

import warnings

import eventlet

warnings.simplefilter('ignore', DeprecationWarning)
from eventlet import processes
warnings.simplefilter('default', DeprecationWarning)

from tests import LimitedTestCase, main, skip_on_windows


class TestEchoPool(LimitedTestCase):
    def setUp(self):
        super(TestEchoPool, self).setUp()
        self.pool = processes.ProcessPool('echo', ["hello"])

    @skip_on_windows
    def test_echo(self):
        result = None

        proc = self.pool.get()
        try:
            result = proc.read()
        finally:
            self.pool.put(proc)
        self.assertEqual(result, b'hello\n')

    @skip_on_windows
    def test_read_eof(self):
        proc = self.pool.get()
        try:
            proc.read()
            self.assertRaises(processes.DeadProcess, proc.read)
        finally:
            self.pool.put(proc)

    @skip_on_windows
    def test_empty_echo(self):
        p = processes.Process('echo', ['-n'])
        self.assertEqual(b'', p.read())
        self.assertRaises(processes.DeadProcess, p.read)


class TestCatPool(LimitedTestCase):
    def setUp(self):
        super(TestCatPool, self).setUp()
        eventlet.sleep(0)
        self.pool = processes.ProcessPool('cat')

    @skip_on_windows
    def test_cat(self):
        result = None

        proc = self.pool.get()
        try:
            proc.write(b'goodbye')
            proc.close_stdin()
            result = proc.read()
        finally:
            self.pool.put(proc)

        self.assertEqual(result, b'goodbye')

    @skip_on_windows
    def test_write_to_dead(self):
        proc = self.pool.get()
        try:
            proc.write(b'goodbye')
            proc.close_stdin()
            proc.read()
            self.assertRaises(processes.DeadProcess, proc.write, 'foo')
        finally:
            self.pool.put(proc)

    @skip_on_windows
    def test_close(self):
        proc = self.pool.get()
        try:
            proc.write(b'hello')
            proc.close()
            self.assertRaises(processes.DeadProcess, proc.write, 'goodbye')
        finally:
            self.pool.put(proc)


class TestDyingProcessesLeavePool(LimitedTestCase):
    def setUp(self):
        super(TestDyingProcessesLeavePool, self).setUp()
        self.pool = processes.ProcessPool('echo', ['hello'], max_size=1)

    @skip_on_windows
    def test_dead_process_not_inserted_into_pool(self):
        proc = self.pool.get()
        try:
            try:
                result = proc.read()
                self.assertEqual(result, b'hello\n')
                result = proc.read()
            except processes.DeadProcess:
                pass
        finally:
            self.pool.put(proc)
        proc2 = self.pool.get()
        assert proc is not proc2


if __name__ == '__main__':
    main()

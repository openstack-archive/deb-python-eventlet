import tests


class Socket(tests.LimitedTestCase):
    def test_patched_thread(self):
        env = {'EVENTLET_TPOOL_DNS': 'yes'}
        output = tests.run_python('tests/env_test_socket_getaddrinfo.py', env=env)
        lines = output.splitlines()
        self.assertEqual(len(lines), 2, lines)


class Tpool(tests.LimitedTestCase):
    longMessage = True
    maxDiff = None

    @tests.skip_with_pyevent
    def test_tpool_size_default(self):
        # modify this together with default value in eventlet.tpool
        expected = 20
        env = {'eventlet_test_limit': str(expected + 20)}
        output = tests.run_python('tests/env_test_tpool_size.py', env=env)
        lines = output.splitlines()
        self.assertEqual(len(lines), 1, output)
        highwater = int(output.strip())
        self.assertEqual(highwater, expected, output)

    @tests.skip_with_pyevent
    def test_tpool_size_custom(self):
        expected = 40
        env = {
            'EVENTLET_THREADPOOL_SIZE': str(expected),
            'eventlet_test_limit': str(expected + 20),
        }
        output = tests.run_python('tests/env_test_tpool_size.py', env=env)
        lines = output.splitlines()
        self.assertEqual(len(lines), 1, output)
        highwater = int(output.strip())
        self.assertEqual(highwater, expected, output)

    def test_tpool_negative(self):
        env = {'EVENTLET_THREADPOOL_SIZE': '-1'}
        output = tests.run_python('tests/env_test_tpool_size.py', env=env)
        lines = output.splitlines()
        self.assert_(len(lines) > 1, output)
        highwater = int(lines[-1])
        self.assert_('AssertionError' in output, output)
        self.assertEqual(highwater, 0, output)

    def test_tpool_zero(self):
        env = {'EVENTLET_THREADPOOL_SIZE': '0'}
        output = tests.run_python('tests/env_test_tpool_size.py', env=env)
        lines = output.splitlines()
        self.assert_(len(lines) > 1, output)
        self.assert_('Warning' in output, output)
        self.assertEqual(lines[-1], '1', output)


class Hub(tests.LimitedTestCase):

    def test_eventlet_hub(self):
        for hub in ('selects',):
            env = {'EVENTLET_HUB': 'selects'}
            output = tests.run_python('tests/env_test_hub.py', env=env)
            lines = output.splitlines()
            self.assertEqual(len(lines), 1, output)
            self.assert_(hub in output, output)

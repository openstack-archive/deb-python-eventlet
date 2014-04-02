import tests


class TestImportPatched(tests.LimitedTestCase):
    def test_patch_a_module(self):
        output = tests.run_python('tests/patcher_test_import_module.py')
        lines = output.splitlines()
        assert lines[0].startswith('patcher'), output
        assert lines[1].startswith('base'), output
        assert lines[2].startswith('importing'), output
        assert 'eventlet.green.socket' in lines[1], output
        assert 'eventlet.green.urllib' in lines[1], output
        assert 'eventlet.green.socket' in lines[2], output
        assert 'eventlet.green.urllib' in lines[2], output
        assert 'eventlet.green.httplib' not in lines[2], output

    def test_import_patched_defaults(self):
        output = tests.run_python('tests/patcher_test_import_defaults.py')
        lines = output.splitlines()
        assert lines[0].startswith('base'), output
        assert lines[1].startswith('defaults'), output
        assert 'eventlet.green.socket' in lines[1], output
        assert 'GreenSocket' in lines[1], output


class TestMonkeyPatch(tests.LimitedTestCase):
    def test_patched_modules(self):
        output = tests.run_python('tests/patcher_test_monkey_patched_modules.py')
        lines = output.splitlines()
        assert len(lines) > 0, output
        assert lines[0].startswith('child'), output
        assert lines[0].count('GreenSocket') == 2, output

    def test_early_patching(self):
        output = tests.run_python('tests/patcher_test_monkey_early_patching.py')
        assert output == u'ok\n'

    def test_late_patching(self):
        output = tests.run_python('tests/patcher_test_monkey_late_patching.py')
        assert output == u'ok\n'

    def test_typeerror(self):
        output = tests.run_python('tests/patcher_test_monkey_typeerror.py')
        assert "TypeError: monkey_patch() got an unexpected keyword argument 'finagle'" in output, output

    def assert_boolean_logic(self, call, expected, not_expected=''):
        env = {
            'call': call,
            'expected': expected,
            'not_expected': not_expected,
        }
        output = tests.run_python('tests/patcher_test_assert_boolean_logic.py', env=env)
        lines = output.splitlines()
        assert len(lines) > 0, output
        ap = 'already_patched'
        assert lines[0].startswith(ap), output
        patched_modules = lines[0][len(ap):].strip()
        # psycopg might or might not be patched based on installed modules
        patched_modules = patched_modules.replace("psycopg,", "")
        # ditto for MySQLdb
        patched_modules = patched_modules.replace("MySQLdb,", "")
        self.assertEqual(
            patched_modules, expected,
            "Logic:%s\nExpected: %s != %s" % (call, expected, patched_modules))

    def test_boolean(self):
        self.assert_boolean_logic("patcher.monkey_patch()",
                                  'os,select,socket,thread,time')

    def test_boolean_all(self):
        self.assert_boolean_logic("patcher.monkey_patch(all=True)",
                                  'os,select,socket,thread,time')

    def test_boolean_all_single(self):
        self.assert_boolean_logic("patcher.monkey_patch(all=True, socket=True)",
                                  'os,select,socket,thread,time')

    def test_boolean_all_negative(self):
        self.assert_boolean_logic(
            "patcher.monkey_patch(all=False, socket=False, select=True)",
            'select')

    def test_boolean_single(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=True)",
                                  'socket')

    def test_boolean_double(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=True, select=True)",
                                  'select,socket')

    def test_boolean_negative(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=False)",
                                  'os,select,thread,time')

    def test_boolean_negative2(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=False, time=False)",
                                  'os,select,thread')

    def test_conflicting_specifications(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=False, select=True)",
                                  'select')


class TestTpool(tests.LimitedTestCase):
    TEST_TIMEOUT = 3

    @tests.skip_with_pyevent
    def test_simple(self):
        output = tests.run_python('tests/patcher_test_tpool_simple.py')
        lines = output.splitlines()
        assert len(lines) == 2, output
        assert lines == ['child 2', 'child 3'], output

    @tests.skip_with_pyevent
    def test_patched_thread(self):
        output = tests.run_python('tests/patcher_test_tpool_patched_thread.py')
        assert output == u'1000\n', output

    @tests.skip_with_pyevent
    def test_unpatched_thread(self):
        output = tests.run_python('tests/patcher_test_tpool_unpatched_thread.py')
        assert output == u'1000\n', output


class TestSubprocess(tests.LimitedTestCase):
    def test_monkeypatched_subprocess(self):
        output = tests.run_python('tests/patcher_test_subprocess_monkey_patched.py')
        assert output == u'done\n', output


class TestThreading(tests.LimitedTestCase):
    def test_original(self):
        output = tests.run_python('tests/patcher_test_threading_original.py')
        lines = output.splitlines()
        assert len(lines) == 3, output
        assert lines[0].startswith('<Thread'), lines[0]
        assert lines[1] == '1', lines[1]
        assert lines[2] == '1', lines[2]

    def test_patched(self):
        output = tests.run_python('tests/patcher_test_threading_patched.py')
        lines = output.splitlines()
        assert len(lines) == 2, output
        assert lines[0].startswith('<_MainThread'), lines[0]
        assert lines[1] == '1', lines[1]

    def test_tpool(self):
        output = tests.run_python('tests/patcher_test_threading_tpool.py')
        lines = output.splitlines()
        assert len(lines) == 2, output
        assert lines[0].startswith('<Thread'), lines[0]
        assert lines[1] == '1', lines[1]

    def test_greenlet(self):
        output = tests.run_python('tests/patcher_test_threading_greenlet.py')
        lines = output.splitlines()
        assert len(lines) == 2, output
        assert lines[0].startswith('<_MainThread'), lines[0]
        assert lines[1] == '1', lines[1]

    def test_greenthread(self):
        output = tests.run_python('tests/patcher_test_threading_greenthread.py')
        lines = output.splitlines()
        assert len(lines) == 2, output
        assert lines[0].startswith('<_GreenThread'), lines[0]
        assert lines[1] == '1', lines[1]

    def test_keyerror(self):
        output = tests.run_python('tests/patcher_test_threading_keyerror.py')
        assert output == u'', output


class TestOs(tests.LimitedTestCase):
    def test_waitpid(self):
        output = tests.run_python('tests/patcher_test_os_waitpid.py')
        assert output == u'1\n', output


class TestGreenThreadWrapper(tests.LimitedTestCase):
    prologue = """import eventlet
eventlet.monkey_patch()
import threading
def test():
    t = threading.currentThread()
"""
    epilogue = """
t = eventlet.spawn(test)
t.wait()
"""

    def test_join(self):
        output = tests.run_python('tests/patcher_test_greenthreadwrapper_join.py')
        assert output.startswith('<_GreenThread'), output

    def test_name(self):
        output = tests.run_python('tests/patcher_test_greenthreadwrapper_name.py')
        lines = output.splitlines()
        assert len(lines) == 9, output
        for i in range(0, 3):
            assert lines[i] == "GreenThread-1", lines[i]
        for i in range(3, 6):
            assert lines[i] == "foo", lines[i]
        for i in range(6, 9):
            assert lines[i] == "bar", lines[i]

    def test_ident(self):
        output = tests.run_python('tests/patcher_test_greenthreadwrapper_ident.py')
        lines = output.splitlines()
        assert len(lines) == 2, output
        assert lines[0] == lines[1], output

    def test_is_alive(self):
        output = tests.run_python('tests/patcher_test_greenthreadwrapper_is_alive.py')
        assert output == u'True\nTrue\n', output

    def test_is_daemon(self):
        output = tests.run_python('tests/patcher_test_greenthreadwrapper_is_daemon.py')
        assert output == u'True\nTrue\n', output


def test_importlib_lock():
    output = tests.run_python('tests/patcher_test_importlib_lock.py')
    assert output.rstrip() == b'ok'


if __name__ == '__main__':
    tests.main()

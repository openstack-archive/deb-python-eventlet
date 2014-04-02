import os

from eventlet.support import six
import tests
from tests.db_pool_test import postgres_requirement


class PatchingPsycopg(tests.LimitedTestCase):
    @tests.skip_unless(postgres_requirement)
    def test_psycopg_patched(self):
        dsn = os.environ.get('PSYCOPG_TEST_DSN')
        if dsn is None:
            # construct a non-json dsn for the subprocess
            psycopg_auth = tests.get_database_auth()['psycopg2']
            if isinstance(psycopg_auth, six.string_types):
                dsn = psycopg_auth
            else:
                dsn = " ".join("%s=%s" % (k, v) for k, v in six.iteritems(psycopg_auth))
        env = {'PSYCOPG_TEST_DSN': dsn}
        output = tests.run_python('tests/patcher_psycopg_test_patched.py', env=env)
        lines = output.splitlines()
        assert len(lines) > 0, output
        if lines[0].startswith('Psycopg not monkeypatched'):
            print("Can't test psycopg2 patching; it's not installed.")
            return
        # if there's anything wrong with the test program it'll have a stack trace
        assert lines[0].startswith('done'), output

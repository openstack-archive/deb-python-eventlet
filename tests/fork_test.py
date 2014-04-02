import tests


def test_fork_simple():
    output = tests.run_python('tests/fork_test_simple.py', new_tmp=True)
    lines = output.splitlines()
    assert len(lines) == 1, output
    assert lines[0] == 'result done', output

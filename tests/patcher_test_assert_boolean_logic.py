# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import os
    from eventlet import patcher
    from eventlet.support import six

    call = os.environ['call']
    expected = os.environ['expected'].split(',')
    not_expected = os.environ['not_expected'].split(',')

    six.exec_(call)

    for mod in expected:
        assert patcher.is_monkey_patched(mod), mod
    for mod in not_expected:
        assert not patcher.is_monkey_patched(mod), mod
    print("already_patched {0}".format(",".join(sorted(patcher.already_patched.keys()))))

# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch(time=False, thread=True)

    import patcher_test_tpool_util
    patcher_test_tpool_util.check_tpool_patched()

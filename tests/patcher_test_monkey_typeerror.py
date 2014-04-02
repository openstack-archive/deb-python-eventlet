# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    from eventlet import patcher
    patcher.monkey_patch(finagle=True)

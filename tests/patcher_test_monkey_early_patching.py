# no standard tests in this file, ignore
__test__ = False

from eventlet import patcher
patcher.monkey_patch()
import eventlet
eventlet.sleep(0.01)
print("ok")

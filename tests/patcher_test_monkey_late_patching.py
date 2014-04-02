# no standard tests in this file, ignore
__test__ = False

import eventlet
eventlet.sleep(0.01)
from eventlet import patcher
patcher.monkey_patch()
eventlet.sleep(0.01)
print("ok")

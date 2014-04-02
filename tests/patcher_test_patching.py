# no standard tests in this file, ignore
__test__ = False

from eventlet.green import socket
from eventlet.green import urllib


def prepare():
    from eventlet import patcher
    print('patcher {0} {1}'.format(socket, urllib))
    patcher.inject('patcher_test_base', globals(), ('socket', socket), ('urllib', urllib))

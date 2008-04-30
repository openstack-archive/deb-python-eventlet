"""\
@file util.py
@author Bob Ippolito

Copyright (c) 2005-2006, Bob Ippolito
Copyright (c) 2007, Linden Research, Inc.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
import fcntl
import socket
import errno

try:
    from OpenSSL import SSL
except ImportError:
    class SSL(object):
        class WantWriteError(object):
            pass

        class WantReadError(object):
            pass

        class ZeroReturnError(object):
            pass

        class SysCallError(object):
            pass


def g_log(*args):
    import sys
    import greenlet
    from eventlet.greenlib import greenlet_id
    g_id = greenlet_id()
    if g_id is None:
        if greenlet.getcurrent().parent is None:
            ident = 'greenlet-main'
        else:
            g_id = id(greenlet.getcurrent())
            if g_id < 0:
                g_id += 1 + ((sys.maxint + 1) << 1)
            ident = '%08X' % (g_id,)
    else:
        ident = 'greenlet-%d' % (g_id,)
    print >>sys.stderr, '[%s] %s' % (ident, ' '.join(map(str, args)))


__original_socket__ = socket.socket

def tcp_socket():
    s = __original_socket__(socket.AF_INET, socket.SOCK_STREAM)
    set_nonblocking(s)
    return s


__original_ssl__ = socket.ssl


def wrap_ssl(sock, certificate=None, private_key=None):
    from OpenSSL import SSL
    from eventlet import greenio, util
    context = SSL.Context(SSL.SSLv23_METHOD)
    print certificate, private_key
    if certificate is not None:
        context.use_certificate_file(certificate)
    if private_key is not None:
        context.use_privatekey_file(private_key)
    context.set_verify(SSL.VERIFY_NONE, lambda *x: True)

    ## TODO only do this on client sockets? how?
    connection = SSL.Connection(context, sock)
    connection.set_connect_state()
    return greenio.GreenSocket(connection)

socket_already_wrapped = False
def wrap_socket_with_coroutine_socket():
    global socket_already_wrapped
    if socket_already_wrapped:
        return

    def new_socket(*args, **kw):
        from eventlet import greenio
        s = __original_socket__(*args, **kw)
        set_nonblocking(s)
        return greenio.GreenSocket(s)
    socket.socket = new_socket

    socket.ssl = wrap_ssl
    
    socket_already_wrapped = True


def socket_bind_and_listen(descriptor, addr=('', 0), backlog=50):
    set_reuse_addr(descriptor)
    descriptor.bind(addr)
    descriptor.listen(backlog)
    return descriptor


def set_reuse_addr(descriptor):
    try:
        descriptor.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            descriptor.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) | 1,
        )
    except socket.error:
        pass
    
def set_nonblocking(descriptor):
    if hasattr(descriptor, 'setblocking'):
        # socket
        descriptor.setblocking(0)
    else:
        # fd
        if hasattr(descriptor, 'fileno'):
            fd = descriptor.fileno()
        else:
            fd = descriptor
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    return descriptor

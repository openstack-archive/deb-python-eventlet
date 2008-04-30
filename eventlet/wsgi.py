"""\
@file wsgi.py
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

import errno
import sys
import time
import traceback
import urllib
import socket
import cStringIO
import SocketServer
import BaseHTTPServer

from eventlet import api
from eventlet.httpdate import format_date_time


class Input(object):
    def __init__(self, rfile, content_length, wfile=None, wfile_line=None):
        self.rfile = rfile
        if content_length is not None:
            content_length = int(content_length)
        self.content_length = content_length

        self.wfile = wfile
        self.wfile_line = wfile_line

        self.position = 0

    def read(self, length=None):
        if self.wfile is not None:
            ## 100 Continue
            self.wfile.write(self.wfile_line)
            self.wfile = None
            self.wfile_line = None

        if length is None and self.content_length is not None:
            length = self.content_length - self.position
        if length and length > self.content_length - self.position:
            length = self.content_length - self.position
        if not length:
            return ''
        read = self.rfile.read(length)
        self.position += len(read)
        return read


class HttpProtocol(BaseHTTPServer.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, format, *args):
        self.server.log_message("%s - - [%s] %s" % (
            self.address_string(),
            self.log_date_time_string(),
            format % args))

    def handle_one_request(self):
        try:
            self.raw_requestline = self.rfile.readline()
        except socket.error, e:
            if e[0] != errno.EBADF:
                raise
            self.raw_requestline = ''
    
        if not self.raw_requestline:
            self.close_connection = 1
            return

        if not self.parse_request():
            return

        self.environ = self.get_environ()
        try:
            self.handle_one_response()
        except socket.error, e:
            # Broken pipe, connection reset by peer
            if e[0] in (32, 54):
                pass
            else:
                raise

    def handle_one_response(self):
        headers_set = []
        headers_sent = []
        # set of lowercase header names that were sent
        header_dict = {}

        wfile = self.wfile
        num_blocks = None
        result = None
        use_chunked = False
        
        def write(data, _write=wfile.write):
            towrite = []
            if not headers_set:
                raise AssertionError("write() before start_response()")
            elif not headers_sent:
                status, response_headers = headers_set
                headers_sent.append(1)
                for k, v in response_headers:
                    header_dict[k.lower()] = k
                towrite.append('%s %s\r\n' % (self.protocol_version, status))
                # send Date header?
                if 'date' not in header_dict:
                    towrite.append('Date: %s\r\n' % (format_date_time(time.time()),))
                if num_blocks is not None:
                    towrite.append('Content-Length: %s\r\n' % (len(''.join(result)),))
                elif use_chunked:
                    towrite.append('Transfer-Encoding: chunked\r\n')
                else:
                    towrite.append('Connection: close\r\n')
                    self.close_connection = 1
                for header in response_headers:
                    towrite.append('%s: %s\r\n' % header)
                towrite.append('\r\n')

            if use_chunked:
                ## Write the chunked encoding
                towrite.append("%x\r\n%s\r\n" % (len(data), data))
            else:
                towrite.append(data)
            _write(''.join(towrite))

        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    if headers_sent:
                        # Re-raise original exception if headers sent
                        raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    # Avoid dangling circular ref
                    exc_info = None

            headers_set[:] = [status, response_headers]
            return write

        try:
            result = self.server.app(self.environ, start_response)
        except Exception, e:
            exc = ''.join(traceback.format_exception(*sys.exc_info()))
            print exc
            if not headers_set:
                start_response("500 Internal Server Error", [('Content-type', 'text/plain')])
                write(exc)
                return

        try:
            num_blocks = len(result)
        except (TypeError, AttributeError, NotImplementedError):
            if self.protocol_version == 'HTTP/1.1':
                use_chunked = True
        try:
            try:
                towrite = []
                try:
                    for data in result:
                        if data:
                            towrite.append(data)
                            if reduce(
                                lambda x, y: x + y,
                                map(
                                    lambda x: len(x), towrite)) > 4096:
                                write(''.join(towrite))
                                del towrite[:]
                except Exception, e:
                    exc = traceback.format_exc()
                    print exc
                    if not headers_set:
                        start_response("500 Internal Server Error", [('Content-type', 'text/plain')])
                        write(exc)
                        return
    
                if towrite:
                    write(''.join(towrite))
                if use_chunked:
                    wfile.write('0\r\n\r\n')
                if not headers_sent:
                    write('')
            except Exception, e:
                traceback.print_exc()
        finally:
            if hasattr(result, 'close'):
                result.close()
            if self.environ['eventlet.input'].position < self.environ.get('CONTENT_LENGTH', 0):
                ## Read and discard body
                self.environ['eventlet.input'].read()

    def get_environ(self):
        env = self.server.get_environ()
        env['REQUEST_METHOD'] = self.command
        env['SCRIPT_NAME'] = ''

        if '?' in self.path:
            path, query = self.path.split('?', 1)
        else:
            path, query = self.path, ''
        env['PATH_INFO'] = urllib.unquote(path)
        env['QUERY_STRING'] = query

        if self.headers.typeheader is None:
            env['CONTENT_TYPE'] = self.headers.type
        else:
            env['CONTENT_TYPE'] = self.headers.typeheader

        length = self.headers.getheader('content-length')
        if length:
            env['CONTENT_LENGTH'] = length
        env['SERVER_PROTOCOL'] = 'HTTP/1.0'

        host, port = self.request.getsockname()
        env['SERVER_NAME'] = host
        env['SERVER_PORT'] = str(port)
        env['REMOTE_ADDR'] = self.client_address[0]
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'

        for h in self.headers.headers:
            k, v = h.split(':', 1)
            k = k.replace('-', '_').upper()
            v = v.strip()
            if k in env:
                continue
            envk = 'HTTP_' + k
            if envk in env:
                env[envk] += ',' + v
            else:
                env[envk] = v

        if env.get('HTTP_EXPECT') == '100-continue':
            wfile = self.wfile
            wfile_line = 'HTTP/1.1 100 Continue\r\n\r\n'
        else:
            wfile = None
            wfile_line = None
        env['wsgi.input'] = env['eventlet.input'] = Input(
            self.rfile, length, wfile=wfile, wfile_line=wfile_line)

        return env

    def finish(self):
        BaseHTTPServer.BaseHTTPRequestHandler.finish(self)
        self.connection.close()


class Server(BaseHTTPServer.HTTPServer):
    def __init__(self, socket, address, app, log, environ=None):
        self.socket = socket
        self.address = address
        if log:
            self.log = log
            log.write = log.info
        else:
            self.log = sys.stderr
        self.app = app
        self.environ = environ

    def get_environ(self):
        socket = self.socket
        d = {
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.multithread': True,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'http',
        }
        if self.environ is not None:
            d.update(self.environ)
        return d

    def process_request(self, (socket, address)):
        proto = HttpProtocol(socket, address, self)
        proto.handle()

    def log_message(self, message):
        self.log.write(message + '\n')


def server(sock, site, log=None, environ=None, max_size=None):
    serv = Server(sock, sock.getsockname(), site, log, environ=None)
    try:
        print "wsgi starting up on", sock.getsockname()
        while True:
            try:
                api.spawn(serv.process_request, sock.accept())
            except KeyboardInterrupt:
                api.get_hub().remove_descriptor(sock.fileno())
                print "wsgi exiting"
                break
    finally:
        try:
            sock.close()
        except socket.error, e:
            if e[0] != errno.EPIPE:
                raise

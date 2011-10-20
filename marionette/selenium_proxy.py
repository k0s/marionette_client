import BaseHTTPServer
import json
import re

from marionette import Marionette, HTMLElement

class SeleniumRequestServer(BaseHTTPServer.HTTPServer):

    def __init__(self, marionette, *args, **kwargs):
        self.marionette = marionette
        BaseHTTPServer.HTTPServer.__init__(self, *args, **kwargs)

    def __del__(self):
        if self.marionette.server:
            self.marionette.delete_session()

class SeleniumRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    pathRe = re.compile(r'/session/(.*?)/(.*)')

    def file_not_found(self):
        self.send_response(404)
        self.end_headers()
        self.wfile.write('%s not found' % self.path)

    def send_JSON(self, data=None, session=None):
        if data is None:
            data = {}
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        if not 'status' in data:
            data['status'] = 0
        self.wfile.write(json.dumps(data))

    def do_GET(self):
        print 'GET', self.path
        if self.path == '/status':
            self.send_JSON(data=self.server.marionette.status())
        else:
            self.file_not_found()

    def do_POST(self):
        print 'POST', self.path
        session = None
        path = self.path
        content_len = self.headers.getheader('content-length')
        body = json.loads(self.rfile.read(int(content_len)))
        m = self.pathRe.match(self.path)
        if m:
            session = m.group(1)
            path = '/%s' % m.group(2)
        if path == '/session':
            session = self.server.marionette.start_session()
            # 'value' is the browser capabilities, which we're ignoring for now
            self.send_JSON(data={'sessionId': session,
                                 'value': {}})
        elif path == '/url':
            assert(session)
            assert(self.server.marionette.navigate(body['url']))
            self.send_JSON(data={'sessionId': session})
        else:
            self.file_not_found()


class SeleniumProxy(object):

    def __init__(self, remote_host, remote_port, proxy_port=4444):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.proxy_port = proxy_port

    def start(self):
        marionette = Marionette(self.remote_host, self.remote_port)
        httpd = SeleniumRequestServer(marionette,
                                      ('127.0.0.1', self.proxy_port),
                                      SeleniumRequestHandler)
        httpd.serve_forever()

if __name__ == "__main__":
    proxy = SeleniumProxy('localhost', 2626)
    proxy.start()

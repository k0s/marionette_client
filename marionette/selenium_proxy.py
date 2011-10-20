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

    def send_JSON(self, data=None, session=None, value=None):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        if data is None:
            data = {}
        if not 'status' in data:
            data['status'] = 0
        if session is not None:
            data['sessionId'] = session
        if value is None:
            data['value'] = {}
        else:
            data['value'] = value

        self.wfile.write(json.dumps(data))

    def process_request(self):
        session = body = None
        path = self.path
        m = self.pathRe.match(self.path)
        if m:
            session = m.group(1)
            path = '/%s' % m.group(2)
        content_len = self.headers.getheader('content-length')
        if content_len:
            body = json.loads(self.rfile.read(int(content_len)))
        return path, body, session

    def do_DELETE(self):
        print 'DELETE', self.path

        path, body, session = self.process_request()

        if path == '/window':
            assert(session)
            assert(self.server.marionette.close_window())
            self.send_JSON(session=session)
        else:
            self.file_not_found()

    def do_GET(self):
        print 'GET', self.path

        path, body, session = self.process_request()

        if path == '/status':
            self.send_JSON(data=self.server.marionette.status())
        elif path == '/url':
            assert(session)
            self.send_JSON(value=self.server.marionette.get_url(),
                           session=session)
        elif path == '/window_handle':
            assert(session)
            self.send_JSON(session=session,
                           value=self.server.marionette.get_window())
        elif path == '/window_handles':
            assert(session)
            self.send_JSON(session=session,
                           value=self.server.marionette.get_windows())
        else:
            self.file_not_found()

    def do_POST(self):
        print 'POST', self.path

        path, body, session = self.process_request()

        if path == '/back':
            assert(session)
            assert(self.server.marionette.go_back())
            self.send_JSON(session=session)
        elif path == '/element':
            # find element variants
            assert(session)
            self.send_JSON(session=session,
                           value={'ELEMENT': str(self.server.marionette.find_element(body['using'], body['value']))})
        elif path == '/execute':
            assert(session)
            if body['args']:
                result = self.server.marionette.execute_script(body['script'], script_args=body['args'])
            else:
                result = self.server.marionette.execute_script(body['script'])
            self.send_JSON(session=session, value=result)
        elif path == '/execute_async':
            assert(session)
            if body['args']:
                result = self.server.marionette.execute_async_script(body['script'], script_args=body['args'])
            else:
                result = self.server.marionette.execute_async_script(body['script'])
            self.send_JSON(session=session, value=result)
        elif path == '/forward':
            assert(session)
            assert(self.server.marionette.go_forward())
            self.send_JSON(session=session)
        elif path == '/refresh':
            assert(session)
            assert(self.server.marionette.refresh())
            self.send_JSON(session=session)
        elif path == '/session':
            session = self.server.marionette.start_session()
            # 'value' is the browser capabilities, which we're ignoring for now
            self.send_JSON(session=session, value={})
        elif path == '/timeouts/async_script':
            assert(session)
            assert(self.server.marionette.set_script_timeout(body['ms']))
            self.send_JSON(session=session)
        elif path == '/timeouts/implicit_wait':
            assert(session)
            assert(self.server.marionette.set_search_timeout(body['ms']))
            self.send_JSON(session=session)
        elif path == '/url':
            assert(session)
            assert(self.server.marionette.navigate(body['url']))
            self.send_JSON(session=session)
        elif path == '/window':
            assert(session)
            assert(self.server.marionette.switch_window(body['name']))
            self.send_JSON(session=session)
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

from client import MarionetteClient

class HTMLElement(object):

    CLASS = "class name"
    SELECTOR = "css selector"
    ID = "id"
    NAME = "name"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    TAG = "tag name"
    XPATH = "xpath"

    def __init__(self, marionette, id):
        self.marionette = marionette
        self.id = id

    def __str__(self):
        return self.id

    def equals(self, other_element):
        return self.marionette._send_message('elementsEqual', 'value', elements=[self.id, other_element.id])

    def find_element(self, method, target):
        return self.marionette.find_element(method, target, self.id)

    def find_elements(self, method, target):
        return self.marionette.find_elements(method, target, self.id)

    def click(self):
        return self.marionette._send_message('clickElement', 'ok', element=self.id)

    def text(self):
        return self.marionette._send_message('getElementText', 'value', element=self.id)

    def send_keys(self, string):
        return self.marionette._send_message('sendKeysToElement', 'ok', element=self.id, value=string)

    def value(self):
        return self.marionette._send_message('getElementValue', 'value', element=self.id)

    def clear(self):
        return self.marionette._send_message('clearElement', 'ok', element=self.id)

    def selected(self):
        return self.marionette._send_message('isElementSelected', 'value', element=self.id)

    def enabled(self):
        return self.marionette._send_message('isElementEnabled', 'value', element=self.id)

    def displayed(self):
        return self.marionette._send_message('isElementDisplayed', 'value', element=self.id)


class Marionette(object):

    def __init__(self, host='localhost', port=2626):
        self.host = host
        self.port = port
        self.client = MarionetteClient(self.host, self.port)
        self.actor = 'marionette'
        self.session = None
        self.window = None

    def _send_message(self, command, response_key, **kwargs):
        if not self.session and command not in ('newSession', 'getStatus'):
            self.start_session()

        message = { 'to': self.actor,
                    'command': command }
        if self.session:
            message['session'] = self.session
        if kwargs:
            message.update(kwargs)

        response = self.client.send(message)

        if (response_key == 'ok' and response.get('ok') ==  True) or response_key in response:
            return response[response_key]
        else:
            self._handle_error(response)

    def _handle_error(self, response):
        raise Exception(response)

    def status(self):
        return self._send_message('getStatus', 'value')

    def start_session(self, desired_capabilities=None):
        # We are ignoring desired_capabilities, at least for now.
        self.session = self._send_message('newSession', 'value')
        return self.session

    def delete_session(self):
        response = self._send_message('deleteSession', 'ok')
        self.session = None
        self.window = None
        self.client.close()
        return response

    def get_session_capabilities(self):
        response = self._send_message('getSessionCapabilities', 'value')
        return response

    def set_script_timeout(self, timeout):
        response = self._send_message('setScriptTimeout', 'ok', value=timeout)
        return response

    def set_search_timeout(self, timeout):
        response = self._send_message('setSearchTimeout', 'ok', value=timeout)
        return response

    def get_window(self):
        self.window = self._send_message('getWindow', 'value')
        return self.window

    def get_windows(self):
        response = self._send_message('getWindows', 'values')
        return response

    def close_window(self, window_id=None):
        if not window_id:
            window_id = self.get_window()
        response = self._send_message('closeWindow', 'ok', value=window_id)
        return response

    def switch_window(self, window_id):
        response = self._send_message('switchToWindow', 'ok', value=window_id)
        self.window = window_id
        return response

    def get_url(self):
        response = self._send_message('getUrl', 'value')
        return response

    def navigate(self, url):
        response = self._send_message('goUrl', 'ok', value=url)
        return response

    def go_back(self):
        response = self._send_message('goBack', 'ok')
        return response

    def go_forward(self):
        response = self._send_message('goForward', 'ok')
        return response

    def refresh(self):
        response = self._send_message('refresh', 'ok')
        return response

    def execute_script(self, script, script_args=None):
        if script_args is None:
            script_args = []
        response = self._send_message('executeScript', 'value', value=script, args=script_args)
        return response

    def execute_async_script(self, script, script_args=None):
        if script_args is None:
            script_args = []
        response = self._send_message('executeAsyncScript', 'value', value=script, args=script_args)
        return response

    def find_element(self, method, target, id=None):
        kwargs = { 'value': target, 'using': method }
        if id:
            kwargs['element'] = id
        response = self._send_message('findElement', 'value', **kwargs)
        element = HTMLElement(self, response)
        return element

    def find_elements(self, method, target, id=None):
        kwargs = { 'value': target, 'using': method }
        if id:
            kwargs['element'] = id
        response = self._send_message('findElements', 'values', **kwargs)
        assert(isinstance(response, list))
        elements = []
        for x in response:
            elements.append(HTMLElement(self, x))
        return elements


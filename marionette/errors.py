
class MarionetteException(Exception):

    def __init__(self, message=None, status=500, stacktrace=None):
        self.message = message
        self.status = status
        self.stacktrace = stacktrace

class TimeoutException(MarionetteException):
    pass

class JavascriptException(MarionetteException):
    pass

class NoSuchElementException(MarionetteException):
    pass

class XPathLookupException(MarionetteException):
    pass

class NoSuchWindowException(MarionetteException):
    pass

class StaleElementException(MarionetteException):
    pass

class ScriptTimeoutException(MarionetteException):
    pass

class ElementNotVisibleException(MarionetteException):
    pass

class NoSuchFrameException(MarionetteException):
    pass

import threading

try:
    from selenium import webdriver
except:
    print 'requires selenium Python bindings; pip install selenium'
    raise
from selenium_proxy import SeleniumProxy
from testserver import TestServer

if __name__ == '__main__':
    # start the test server on port 2626
    server = TestServer(2626)
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()

    # Start the selenium proxy on port 4444, connecting to the test server
    # on port 2626.
    proxy = SeleniumProxy('127.0.0.1', 2626, proxy_port=4444)
    proxy_thread = threading.Thread(target=proxy.start)
    proxy_thread.daemon = True
    proxy_thread.start()

    # invoke selenium commands as tests
    driver = webdriver.Remote(command_executor='http://127.0.0.1:4444',
                              desired_capabilities=webdriver.DesiredCapabilities.FIREFOX)
    assert(driver)
    driver.get('http://www.mozilla.org')
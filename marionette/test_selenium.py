import threading

try:
    from selenium import webdriver
    from selenium.webdriver.remote.webelement import WebElement
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

    driver.get(TestServer.TEST_URL)
    assert(driver.current_url == TestServer.TEST_URL)
    driver.back()
    driver.forward()
    driver.refresh()

    driver.set_script_timeout(10) # in selenium the number is in seconds
    driver.implicitly_wait(10)    # ditto

    assert(TestServer.TEST_EXECUTE_RETURN_VALUE == driver.execute_script(TestServer.TEST_EXECUTE_SCRIPT))
    assert(TestServer.TEST_EXECUTE_RETURN_VALUE == driver.execute_script(TestServer.TEST_EXECUTE_SCRIPT,
                                                                         TestServer.TEST_EXECUTE_SCRIPT_ARGS))
    assert(TestServer.TEST_EXECUTE_RETURN_VALUE == driver.execute_async_script(TestServer.TEST_EXECUTE_SCRIPT))
    assert(TestServer.TEST_EXECUTE_RETURN_VALUE == driver.execute_async_script(TestServer.TEST_EXECUTE_SCRIPT,
                                                                               TestServer.TEST_EXECUTE_SCRIPT_ARGS))

    # The return values for all find_element_XXX methods should be a WebElement
    # object, which has an 'id' property that contains the element's ID.
    element = driver.find_element_by_name('foo')
    assert(isinstance(element, WebElement))
    assert(element.id == TestServer.TEST_FIND_ELEMENT)
    element = driver.find_element_by_id('foo')
    assert(isinstance(element, WebElement))
    assert(element.id == TestServer.TEST_FIND_ELEMENT)
    element = driver.find_element_by_xpath('foo')
    assert(isinstance(element, WebElement))
    assert(element.id == TestServer.TEST_FIND_ELEMENT)
    element = driver.find_element_by_link_text('foo')
    assert(isinstance(element, WebElement))
    assert(element.id == TestServer.TEST_FIND_ELEMENT)
    element = driver.find_element_by_partial_link_text('foo')
    assert(isinstance(element, WebElement))
    assert(element.id == TestServer.TEST_FIND_ELEMENT)
    element = driver.find_element_by_tag_name('foo')
    assert(isinstance(element, WebElement))
    assert(element.id == TestServer.TEST_FIND_ELEMENT)
    element = driver.find_element_by_class_name('foo')
    assert(isinstance(element, WebElement))
    assert(element.id == TestServer.TEST_FIND_ELEMENT)
    element = driver.find_element_by_css_selector('foo')
    assert(isinstance(element, WebElement))
    assert(element.id == TestServer.TEST_FIND_ELEMENT)

    assert(driver.current_window_handle == TestServer.TEST_CURRENT_WINDOW)
    assert(driver.window_handles == TestServer.TEST_WINDOW_LIST)
    driver.switch_to_window(TestServer.TEST_CURRENT_WINDOW)
    driver.close() # this is close_window

    print 'Tests complete!'


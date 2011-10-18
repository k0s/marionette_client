import threading
from testserver import TestServer
from marionette import Marionette, HTMLElement

if __name__ == '__main__':

    # start the test server
    server = TestServer(2626)
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()

    # run some trivial unit tests which just verify the protocol
    m = Marionette(host='localhost', port=2626)
    assert(m.status()['os']['arch'] == 'x86')
    assert(m.start_session())
    assert(m.get_session_capabilities()['javascriptEnabled'] == True)
    assert(m.get_window() == 'window1')
    assert(m.window == 'window1')
    assert(m.get_windows() == ['window1', 'window2', 'window3'])
    assert(m.switch_window('window2'))
    assert(m.window == 'window2')
    assert(m.close_window('window2'))
    assert(m.set_script_timeout(1000))
    assert(m.set_search_timeout(500))
    assert(m.get_url() == 'http://www.mozilla.org')
    assert(m.navigate('http://www.firefox.com'))
    assert(m.go_back())
    assert(m.go_forward())
    assert(m.refresh())
    assert(m.execute_script('return 10;'))
    assert(m.execute_script('return 10;', ['testing']))
    assert(m.execute_async_script('return 10;'))
    assert(m.execute_async_script('return 10;', ['testing']))
    assert(str(m.find_element(HTMLElement.CLASS, 'heading')) == 'element1')
    assert([str(x) for x in m.find_elements(HTMLElement.TAG, 'p')] == ['element1', 'element2'])
    assert(str(m.find_element(HTMLElement.CLASS, 'heading').find_element(HTMLElement.TAG, 'h1')) == 'element1')
    assert([str(x) for x in m.find_element(HTMLElement.ID, 'div1').find_elements(HTMLElement.SELECTOR, '.main')] == ['element1', 'element2'])
    assert(m.find_element(HTMLElement.ID, 'id1').click())
    assert(m.find_element(HTMLElement.ID, 'id2').text() == 'first name')
    assert(m.find_element(HTMLElement.ID, 'id3').send_keys('Mozilla Firefox'))
    assert(m.find_element(HTMLElement.ID, 'id3').value() == 'Mozilla Firefox')
    assert(m.find_element(HTMLElement.ID, 'id3').clear())
    assert(not m.find_element(HTMLElement.ID, 'id3').selected())
    assert(m.find_element(HTMLElement.ID, 'id1').equals(m.find_element(HTMLElement.TAG, 'p')))
    assert(m.delete_session())
    assert(m.find_element(HTMLElement.ID, 'id3').enabled())
    assert(m.find_element(HTMLElement.ID, 'id3').displayed())

    # verify a session is started automatically for us if needed
    assert(m.get_window() == 'window1')
    assert(m.delete_session())

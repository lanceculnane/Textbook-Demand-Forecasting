from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from pyvirtualdisplay import Display


def get_site(driver, url, delay=20):
    '''
    Input: webdriver object, url to be visited
    5 second conditional delay to wait for full page load
    Returns: webdriver object after it has visited the page.  Should retain cookies.
    '''

    driver.get(url)
    delay = delay
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,'//div[@class="footerLeft"]')))
    return driver

def get_cookies_for_requests(driver):
    '''
    Input: webdriver object
    Returns: dict of cookies required to access
    '''
    all_cookies = driver.get_cookies()
    cookies = {}
    for cookie in all_cookies:
        if ('bncollege.com' in cookie['domain'] and 'TS' in cookie['name']):
            cookies[cookie["name"]] = cookie["value"]
    return cookies

def low_bandwidth_chrome():
    #
    #display = Display(visible=0, size=(1920, 1080))
    #display.start()
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images":2}
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_argument("user-agent={}".format(UserAgent().random))
    #
    #chrome_options.add_argument('--proxy-server=http://127.0.0.1:8118')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from pyvirtualdisplay import Display
from TorCtl import TorCtl

def low_bandwidth_chrome():
    """
    Initiates and returns a headless Chrome webdriver that doesn't load images, has a randomized useragent, and runs through privoxy/tor proxy
    See for headless setup:
    https://christopher.su/2015/selenium-chromedriver-ubuntu/

    """
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images":2}
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_argument("user-agent={}".format(UserAgent().random))
    chrome_options.add_argument('--proxy-server=http://127.0.0.1:8118')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    renew_connection()
    return driver

def renew_connection():
    """
    Renews the connection to the Tor network, in order to get a new exit node with a different IP address
    See for setup details:
    http://lyle.smu.edu/~jwadleigh/seltest/
    http://sacharya.com/crawling-anonymously-with-tor-in-python/
    For setting up privoxy, need to add { -block } to /etc/privoxy/user.action to prevent filtering of urls
    For TorCTL setup in source 2, also need to change /etc/tor/torrc variable about cookies on line after HashedControlPassword to 0
    """
    conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051,passphrase="mypassword")
    conn.send_signal("NEWNYM")
    conn.close()

def get_site(driver, url, delay=10):
    """
    Input: webdriver object, url to be visited
    10 second conditional delay to wait for full page load
    Returns: webdriver object after it has visited the page.
    Customized to looks for bncollege page footers
    """

    driver.get(url)
    delay = delay
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,'//div[@class="footerLeft"]')))
    return driver

def get_cookies_for_requests(driver):
    """
    Input: webdriver object
    Returns: dict of cookies required to access
    """
    all_cookies = driver.get_cookies()
    cookies = {}
    for cookie in all_cookies:
        if ('bncollege.com' in cookie['domain'] and 'TS' in cookie['name']):
            cookies[cookie["name"]] = cookie["value"]
    return cookies

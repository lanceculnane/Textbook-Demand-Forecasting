from fake_useragent import UserAgent
import requests
import os


def start_session(proxy=True):
    """
    Returns a requests session going through privoxy/tor proxy by default.
    Todo: Allow choice of proxy
    """
    session = requests.Session()
    if proxy:
        #username = os.environ['PROXYMESH_USERNAME']
        #password = os.environ['PROXYMESH_PASSWORD']
        #session.auth = (username, password)
        session.proxies = {'http': 'http://127.0.0.1:8118'}


    session.headers = {'User-Agent': UserAgent().random}
    return session

def reset_headers(session):
    """
    Resets the session's headers with a random useragent and returns the session
    """
    session.headers = {'User-Agent': UserAgent().random}
    return session
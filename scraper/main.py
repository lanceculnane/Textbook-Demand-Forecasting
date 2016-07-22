
from fake_useragent import UserAgent
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pyvirtualdisplay import Display
import json
from lxml import html
import re
import pickle
from pymongo import MongoClient
import time
import bookstore_classes as b_c
import bookstore_functions as b_f
import requests_functions as r_f
import selenium_functions as s_f
import general_functions as g_f
import pymongo_functions as p_f
import pandas as pd
from random import shuffle

if __name__=='__main__':
    df = pd.read_csv('store_urls_clean.txt',delimiter='|', header=None, names=['school','url'])
    store_names = df['school'].values
    store_urls = df['url'].values
    session = r_f.start_session(proxy=True)
    client = MongoClient()
    #store_name,store_url = 'Penn State Dubois|http://psudubois.bncollege.com'.split('|')
    #hierarchy = pickle.load(open('test_store.pkl','r'))

    #store.load_from_dict(hierarchy)
    #place = store.resume()
    #place=False
    db = 'test_db'
    for store_name, store_url in zip(store_names,store_urls):
        store = b_c.Bookstore(name=store_name,url=store_url)
        if (p_f.store_complete(client,store, db=db) or b_f.check_multicampus(store,session)):
            continue

        store.load_from_dict(p_f.read_store_from_db(client,store,db = db))
        for i in range(50):
            if not store.structure_complete:
                try:
                    place = store.resume()
                    store = b_f.get_full_bookstore(store, session,store_name,store_url,resume=bool(place),place=place)
                except:
                    print 'something went terribly wrong, iteration {}'.format(i)
                    time.sleep(10)
                finally:
                    p_f.write_store_to_db(client,store, db=db)


        b_f.get_all_books(client,store)
        print ('Finished getting {}'.format(store.name))

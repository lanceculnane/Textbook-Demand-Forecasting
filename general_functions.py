import time
import random
import bookstore_functions as b_f
import pymongo_functions as p_f

def retry(func, params, session, store_url, find_textbooks_url, retries=3, delay=5):
    for attempt in xrange(retries):
        try:
            return func(*params)
        except:
            time.sleep(delay)
            print "Attempt numer {} to complete function {} with parameters {}".format(attempt,func.__name__,params)
            session = b_f.reset_cookies(session,store_url,find_textbooks_url)
    return False

def retry_store(client,bookstore,session, retries=5):
    '''
    for attempt in range retries
        try
            read store from db
            load store, check for resume
            get_full_bookstore
            mark store as done
        except
            write store to mongodb
            wait long time
    '''
    for attempt in range(retries):
        try:
            p_f.read_store_from_db(client,bookstore.ID)
        except:
            print 'somthing'
    return False

def random_sleep(low=0,high=.8):
    duration = random.random()*(high-low)+low
    time.sleep(duration)

def retry_multipurpose(try_func,try_params,except_func,except_params,retries=5):
    for attempt in range(retries):
        try:
            return try_func(try_params)
        except:
            except_func(except_params)
    return False

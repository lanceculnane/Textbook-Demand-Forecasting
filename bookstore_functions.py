from lxml import html
import re
import requests_functions as r_f
import selenium_functions as s_f
import bookstore_classes as b_c
import general_functions as g_f
import pymongo_functions as p_f
import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import time
from collections import OrderedDict
from collections import defaultdict
from fake_useragent import UserAgent
from random import shuffle

def get_find_textbooks_url(session,bookstore_url):
    page = session.get(bookstore_url)
    tree = html.fromstring(page.text)
    find_textbooks_url = tree.xpath('//a[@title="Find Textbooks"]/@href')[0]
    return find_textbooks_url

def get_storeID(find_textbooks_url):
    result = re.search('storeId=(.*)',find_textbooks_url)
    storeID = result.group(1)
    return storeID

def check_multicampus(store,session):
    find_textbooks_url = get_find_textbooks_url(session,store.url)
    #driver = webdriver.Firefox()
    driver = s_f.low_bandwidth_chrome()
    s_f.get_site(driver, store.url)
    s_f.get_site(driver, find_textbooks_url)
    multicampus = driver.find_elements(By.XPATH,'//div[@class="bncbSelectBox campusSectionHeader"]')
    driver.quit()
    return bool(multicampus)

def get_multi_campus_IDs(driver):
    campus_counter = int(driver.find_element(By.XPATH,'//input[@name="campusCounter"]').get_attribute("value"))
    campus_elements = driver.find_elements(By.XPATH,'//li[@class="bncbOptionItem"]')[:campus_counter]
    campuses = []
    for campus_element in campus_elements:
        campuses.append({'categoryId':campus_element.get_attribute("data-optionvalue"), 'categoryName':campus_element.get_attribute('innerText')})
    return campuses

def get_campusID_and_cookies(session, bookstore_url, find_textbooks_url, store_name):
    #driver = webdriver.Firefox()
    driver = s_f.low_bandwidth_chrome()
    s_f.get_site(driver, bookstore_url)
    s_f.get_site(driver, find_textbooks_url)

    multicampus = driver.find_elements(By.XPATH,'//div[@class="bncbSelectBox campusSectionHeader"]')
    if multicampus:
        campuses = get_multi_campus_IDs(driver)
    else:
        campuses =[{'categoryId':driver.find_element(By.XPATH,'//input[@name="campus1"]').get_attribute("value"), 'categoryName':store_name}]
    session.cookies.update(s_f.get_cookies_for_requests(driver))
    all_cookies = driver.get_cookies()
    driver.quit()
    return (campuses, all_cookies)

def get_terms(session, bookstore_url, storeID, campusID):
    parameters = [('campusId', campusID), ('termId', ''), ('deptId', ''), ('courseId', ''), ('sectionId', ''), ('storeId', storeID), ('catalogId', '10001'), ('langId', '-1'), ('dropdown', 'campus')]
    url = bookstore_url + '/webapp/wcs/stores/servlet/TextBookProcessDropdownsCmd'
    page = session.get(url, params=parameters)
    terms = json.loads(page.text)
    return terms

def get_departments(session, bookstore_url,  storeID, campusID, termID):
    parameters = [('campusId', campusID), ('termId', termID), ('deptId', ''), ('courseId', ''), ('sectionId', ''), ('storeId', storeID), ('catalogId', '10001'), ('langId', '-1'), ('dropdown', 'term')]
    url = bookstore_url + '/webapp/wcs/stores/servlet/TextBookProcessDropdownsCmd'
    page = session.get(url,params=parameters)
    departments = json.loads(page.text)
    return departments

def get_courses(session, bookstore_url,  storeID, campusID, termID, deptID):
    parameters = [('campusId', campusID), ('termId', termID), ('deptId', deptID), ('courseId', ''), ('sectionId', ''), ('storeId', storeID), ('catalogId', '10001'), ('langId', '-1'), ('dropdown', 'dept')]
    url = bookstore_url + '/webapp/wcs/stores/servlet/TextBookProcessDropdownsCmd'
    page = session.get(url,params=parameters)
    courses = json.loads(page.text)
    return courses

def get_sections(session, bookstore_url,  storeID, campusID, termID, deptID, courseID):
    parameters = [('campusId', campusID), ('termId', termID), ('deptId', deptID), ('courseId', courseID), ('sectionId', ''), ('storeId', storeID), ('catalogId', '10001'), ('langId', '-1'), ('dropdown', 'course')]
    url = bookstore_url + '/webapp/wcs/stores/servlet/TextBookProcessDropdownsCmd'
    page = session.get(url,params=parameters)
    #print(page.text)
    sections = json.loads(page.text)
    return sections

def reset_cookies(session, store_url, find_textbooks_url):
    #driver = webdriver.Firefox()
    driver = s_f.low_bandwidth_chrome()
    s_f.get_site(driver, store_url)
    s_f.get_site(driver, find_textbooks_url)
    session.cookies.clear()
    session.cookies.update(s_f.get_cookies_for_requests(driver))
    driver.quit()
    return session


def get_full_bookstore(store, session, store_name, store_url, resume=False, place=None, delay=.3):
    find_textbooks_url = get_find_textbooks_url(session,store_url)
    storeID = get_storeID(find_textbooks_url)
    store.add_attributes(store_name, store_url, storeID)
    campuses, all_cookies = get_campusID_and_cookies(session, store_url, find_textbooks_url, store_name)
    store.add_campuses_from_dict(campuses)
    print ('College: ' + store.name)
    for campus in store.campuses:
        if (resume):
            if campus.ID == place:
                resume = False
        else:
            print (' Campus: ' + campus.name)
            terms = g_f.retry(get_terms,(session,store_url,storeID,campus.ID),session,store_url,find_textbooks_url)
            if not terms:
                continue
            campus.add_terms_from_dict(terms)
        for term in campus.terms:
            if (resume):
                if term.ID == place:
                    resume = False
            else:
                print ('  Term: ' + term.name)
                departments = g_f.retry(get_departments,(session,store_url,storeID,campus.ID,term.ID),session,store_url,find_textbooks_url)
                if not departments:
                    continue
                term.add_departments_from_dict(departments)
            for department in term.departments:
                if (resume):
                    if department.ID == place:
                        resume = False
                else:
                    print ('   Department: ' + department.name)
                    session = r_f.reset_headers(session)
                    courses = g_f.retry(get_courses,(session,store_url,storeID,campus.ID,term.ID,department.ID),session,store_url,find_textbooks_url)
                    if not courses:
                        continue
                    department.add_courses_from_dict(courses)
                for course in department.courses:
                    if (resume):
                        if course.ID == place:
                            resume = False
                    else:
                        print ('     Course: ' + course.name)
                        sections = g_f.retry(get_sections,(session,store_url,storeID,campus.ID,term.ID,department.ID,course.ID),session,store_url,find_textbooks_url)
                        if not sections:
                            continue
                        course.add_sections_from_dict(sections)
                        g_f.random_sleep()
    store.structure_complete = 1
    return store


################# Get books functions ###################

def get_section_chunks(store, chunk_size):
    all_chunks = []
    section_ids = store.get_section_ids()
    section_id_count = len(section_ids)
    for i in range(0,section_id_count,chunk_size):
        if (i+chunk_size >= section_id_count):
            chunk = section_ids[i:]
            all_chunks.append(chunk)
        else:
            chunk = section_ids[i:i+chunk_size]
            all_chunks.append(chunk)
    return all_chunks

def get_books_page(store,row_list):
    #row_list = [{'termID':'74847930','department_name':'AA','course_name':'100','section_name':'001','sectionID':'74840757'},{'termID':'74847930','department_name':'ACCTG','course_name':'211','section_name':'002','sectionID':'74840758'}]
    try:
        find_textbooks_url = store.url + '/webapp/wcs/stores/servlet/TBWizardView?catalogId=10001&langId=-1&storeId=' + store.ID


        #driver = webdriver.Firefox()
        driver = s_f.low_bandwidth_chrome()
        driver = s_f.get_site(driver,store.url)
        driver = s_f.get_site(driver, find_textbooks_url)

        add_row_element = driver.find_element_by_xpath('//a[@class="addMoreRows"]')
        for i in range(4,len(row_list)):
            add_row_element.click()
            time.sleep(.3)
        term_elements = driver.find_elements_by_xpath('//div[@class="bncbSelectBox termHeader"]')
        term_option_elements = term_elements[0].find_elements_by_xpath('//ul[@class="termOptions"]//li')
        portioned_term_option_elements = [term_option_elements[i:i+2] for i in range(0,len(term_option_elements),2)]
        department_elements = driver.find_elements_by_xpath('//input[@title="Department Input Box"]')
        course_elements = driver.find_elements_by_xpath('//input[@title="Course Input Box"]')
        section_elements = driver.find_elements_by_xpath('//input[@title="Section Input Box"]')

        for i, row in enumerate(row_list):
            for elem in portioned_term_option_elements[i]:
                if (elem.get_attribute('data-optionvalue') == row['termID']):
                    term_option_element = elem
            fill_row(term_elements[i],term_option_element,department_elements[i],row['department_name'],course_elements[i],row['course_name'],section_elements[i],row['section_name'],driver)
        submission = driver.find_element_by_xpath('//a[@id="findMaterialButton"]')
        submission.click()
        delay=30
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,'//input[@class="largeDisableBtn AddToCartButton"]')))
        tree = html.fromstring(driver.page_source)

    finally:

        driver.quit()
    return tree

def fill_row(term_element,term_option_element,department_element,department_name,course_element,course_name,section_element,section_name,driver):
    delay = 15
    #term_element = driver.find_elements_by_xpath('//div[@class="bncbSelectBox termHeader"]')
    #this needs to be the correctly pre-selected term element, since getting the term options give every single term element
    term_element.click()
    time.sleep(.1)
    term_option_element.click()
    time.sleep(.1)
    #term1_options = term1_element.find_elements_by_xpath('//ul[@class="termOptions"]//li')
    #department = driver.find_element_by_xpath('//input[@title="Department Input Box"]')

    department_element.send_keys(department_name)
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,'//li[@class="deptColumn"]/ul[@class="better-autocomplete"]/li[@aria-role="menuitem"]')))
    department_options = driver.find_elements_by_xpath('//li[@class="deptColumn"]/ul[@class="better-autocomplete"]/li[@aria-role="menuitem"]')
    for option in department_options:
        #print option.text, option.get_attribute('value'), department_name
        if option.text==department_name:
            option.click()
            break
    time.sleep(.1)

    #course = driver.find_element_by_xpath('//input[@title="Course Input Box"]')

    course_element.send_keys(course_name)
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,'//li[@class="courseColumn"]/ul[@class="better-autocomplete"]/li[@aria-role="menuitem"]')))
    course_options = driver.find_elements_by_xpath('//li[@class="courseColumn"]/ul[@class="better-autocomplete"]/li[@aria-role="menuitem"]')
    for option in course_options:
        if option.text==course_name:
            option.click()
            break
    time.sleep(.1)
    #section = driver.find_element_by_xpath('//input[@title="Section Input Box"]')
    #section keys are sometimes jumbled by aria autocomplete

    '''
    section_options = driver.find_elements_by_xpath('//li[@class="sectionColumn"]/ul[@class="better-autocomplete"]/li[@aria-role="menuitem"]')
    for option in section_options:
        print option.text, section_name
        if option.text==section_name:
            option.click()
    '''
    print ('filling row!')
    for i in range(20):
        section_element.clear()
        section_element.send_keys(section_name)
        time.sleep(.1)
        section_element.send_keys(Keys.ENTER)
        time.sleep(.1)
        if section_element.get_attribute('data-section') == section_name:
            break

    return 1
"""
def get_books_page(store, sectionIDs):
    print ('getting page')

    base_url = store.url + '/webapp/wcs/stores/servlet/BNCBTBListView?catalogId=10001&langId=-1&storeID=' + store.ID + '&campusId=undefined&&'
    find_textbooks_url = store.url + '/webapp/wcs/stores/servlet/TBWizardView?catalogId=10001&langId=-1&storeId=' + store.ID
    for i in range(len(sectionIDs)):
        base_url = base_url +'&section_'+str(i+1)+'='+sectionIDs[i]
    print (base_url)
    #http://stackoverflow.com/questions/26566799/selenium-python-how-to-wait-until-the-page-is-loaded
    '''
    service_args = ['--load-images=false']
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.04")
    dcap['phantomjs.page.customHeaders.referer'] = (find_textbooks_url)
    dcap['phantomjs.page.customHeaders.Host'] = ('psudubois.bncollege.com')
    driver = webdriver.PhantomJS(service_args = service_args,desired_capabilities=dcap)
    '''
    try:
        driver = webdriver.Firefox()
        driver = s_f.get_site(driver,store.url)
        driver.save_screenshot('1.png')
        driver = s_f.get_site(driver, find_textbooks_url)
        driver.save_screenshot('2.png')
        driver = s_f.get_site(driver,base_url)
        driver.save_screenshot('3.png')
        page_source = driver.page_source
        tree = html.fromstring(page_source)
    except:
        driver.save_screenshot('error.png')
    #finally:
        #driver.quit()
    return tree
"""

def get_book_prices(section, book_id, response_tree):
    book_prices=[]
    rent_used = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]//div[@data-textbook-id="{}"]//ul[@class="cm_tb_bookList"]/li[@title="RENT USED"]/span[@class="bookPrice"]/@title'.format(section, book_id))
    book_prices.append(str(rent_used[0]) if rent_used else [])

    rent_new = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]//div[@data-textbook-id="{}"]//ul[@class="cm_tb_bookList"]/li[@title="RENT NEW"]/span[@class="bookPrice"]/@title'.format(section, book_id))
    book_prices.append(str(rent_new[0]) if rent_new else [])

    buy_used = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]//div[@data-textbook-id="{}"]//ul[@class="cm_tb_bookList"]/li[@title="BUY USED "]/span[@class="bookPrice"]/@title'.format(section, book_id))
    book_prices.append(str(buy_used[0]) if buy_used else [])

    buy_new = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]//div[@data-textbook-id="{}"]//ul[@class="cm_tb_bookList"]/li[@title="BUY NEW "]/span[@class="bookPrice"]/@title'.format(section, book_id))
    book_prices.append(str(buy_new[0]) if buy_new else [])

    #book_prices = {"rent_used":rent_used, "rent_new":rent_new, "buy_used":buy_used, "buy_new":buy_new}
    #book_prices = [rent_used[0], rent_new[0],buy_used[0],buy_new[0]]
    for i,price in enumerate(book_prices):
        if (not price):
            book_prices[i] = 'nan'

    return book_prices

def get_book_data(row_list, response_tree):
    sectionID_list = [section['sectionID'] for section in row_list]
    #print ('getting books')
    all_sections = []
    for section in sectionID_list:
        this_section = {section:[]}
        isbns = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]//li[strong="ISBN:"]/text()'.format(str(section)))
        #print isbns
        recommended_type = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]//span[@class="recommendBookType"]/text()'.format(str(section)))
        titles = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]//div[@class="book_desc1 cm_tb_bookInfo"]/h1/a/@title'.format(str(section)))
        authors = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]//div[@class="book_desc1 cm_tb_bookInfo"]/h2//i/text()'.format(str(section)))
        editions = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]//li[@class="book_c1" and contains(strong,"EDITION:")]/text()'.format(str(section)))
        publishers = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]//li[@class="book_c2" and contains(strong,"PUBLISHER:")]/text()'.format(str(section)))
        textbook_ids = response_tree.xpath('//div[@class="book_sec" and @data-section-id={}]//div[@class="book-list"]/div[@class="book_details clearfix cm_tb_details padding_important"]/@data-textbook-id'.format(str(section)))

        prices=[]
        for category in (isbns, editions, publishers,recommended_type):
            for i in range(len(category)):
                category[i] = category[i].encode('utf-8').strip()
        #isbns = [isbn.encode('utf-8').strip() for isbn in isbns]
        isbns = list(filter(None, isbns))
        titles = list(filter(None, titles))
        authors = list(filter(None, authors))
        editions = list(filter(None, editions))
        publishers = list(filter(None, publishers))
        recommended_type = list(filter(None, recommended_type))

        '''
        print ('isbns:',isbns, len(isbns))
        print ('titles:',titles, len(titles))
        print ('authors:',authors, len(authors))
        print ('editions:', editions, len(editions))
        print ('publishers:', publishers, len(publishers))
        '''


        for i in range(len(isbns)):
            isbns[i] = isbns[i].decode('utf-8').strip()
            titles[i] = titles[i].decode('utf-8').strip()
            authors[i] = authors[i].decode('utf-8').strip()[3:]
            editions[i] = editions[i].decode('utf-8').strip()
            publishers[i] = publishers[i].decode('utf-8').strip()
            recommended_type[i] = recommended_type[i].decode('utf-8').strip()
            if (recommended_type[i] == ''):
                recommended_type[i] = "NO DATA"
            prices.append(get_book_prices(section, textbook_ids[i], response_tree))
            this_section[section].append( {"isbn":isbns[i],"rec_type":recommended_type[i], "title":titles[i], "author":authors[i], "edition":editions[i], "publisher":publishers[i], "rent_used":prices[i][0], "rent_new":prices[i][1], "buy_used":prices[i][2], "buy_new":prices[i][3]})
        if not this_section[section]:
            this_section[section] = [{"isbn":'',"rec_type":'', "title":'', "author":'', "edition":'', "publisher":'', "rent_used":'', "rent_new":'', "buy_used":'', "buy_new":''}]
        """
        for sec in this_section:
            for price in ('rent_new', 'rent_used', 'buy_used', 'buy_new'):
                if sec[price] == 'nan':
                    sec.pop(price)
        """
        all_sections.append(this_section)
        '''
        print ('section:', section)
        for i in range(len(books)):
        	print ('isbn:', books[i].strip(), recommended_type[i].strip())

        if (len(books)==0):
        	print ('No books assigned')
        '''
    return all_sections

def get_all_books(client,store):
    for i in range(20):
        try:
            row_lists = store.get_row_lists(chunk_size=25)
            all_section_books = []
            for j,row_list in enumerate(row_lists):
                print('Getting book page # {} of {}'.format(j,len(row_lists)))
                response_tree = get_books_page(store,row_list)
                data = get_book_data(row_list,response_tree)
                for section in data:
                    all_section_books.append(section)
                time.sleep(5)
            #if store completes:
            store.books_complete = 1
            #store.add_books_from_dict(all_section_books)
            #p_f.write_store_to_db(client,store)
        except:
            print('Retry number {} for get_all_books'.format(i+1))
            time.sleep(20)
        finally:
            store.add_books_from_dict(all_section_books)
            p_f.write_store_to_db(client,store)
    return 1

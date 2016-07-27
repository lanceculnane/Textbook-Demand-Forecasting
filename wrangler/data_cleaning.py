from pymongo import MongoClient
import pickle
import pandas as pd

def categorize_terms(client,db='test_db2'):
    """
    Renames terms for consistency.  will need more labels in the future, including an 'Unknown' label
    """
    collection = client[db].stores
    cursor = collection.find({'structure_complete':1,'books_complete':1},modifiers={"$snapshot": True})

    for store in cursor:
        for campus in store['campuses']:
            for term in campus['terms']:
                term_name = str(term['term_name']).upper()
                if '16' in term_name:
                    if 'FALL' in term_name:
                        term_name = 'FALL 2016'
                    elif 'SPRING' in term_name:
                        term_name = 'SPRING 2016'
                    elif 'SUMMER' in term_name:
                        term_name = 'SUMMER 2016'
                term['term_name'] = term_name
        collection.update_one(
            #{ '$unwind': '$campuses'},
            #{ '$unwind': '$campuses.terms'},
            {
            '_id': store['_id']
            },
            {'$set':{
                    'campuses':store['campuses']
                    }
            },
            upsert=False
        )

def convert_book_data(client,db='test_db2'):
    """
    Converts book prices from string to float
    """
    collection = client[db].stores
    cursor = collection.find({'structure_complete':1,'books_complete':1},modifiers={"$snapshot": True})
    #rec_types = ['REQUIRED','REQUIRED PACKAGE','RECOMMENDED','RECOMMENDED PACKAGE','BOOKSTORE RECOMMENDED','PACKAGE COMPONENT','']
    for store in cursor:
        print store['store_name']
        for campus in store['campuses']:
            for term in campus['terms']:
                for department in term['departments']:
                    for course in department['courses']:
                        for section in course['sections']:
                            for book in section['books']:
                                prices = [book['buy_used'],book['buy_new'],book['rent_used'],book['rent_new']]
                                purchase_types = ['buy_used','buy_new','rent_used','rent_new']
                                new_prices = []
                                #isbn = book['isbn']
                                #rec_type = book['rec_type']
                                # if no book info, remove book from db
                                if (len(prices) == 0 or prices[0]==''):
                                    section['books'] = []
                                    continue
                                for purchase_type,price in zip(purchase_types,prices):
                                    if price == 'nan':
                                        new_prices.append(-1)
                                    elif (isinstance(price,float) or isinstance(price,int)):
                                        new_prices.append(price)
                                    else:

                                        new_prices.append(float(price.strip('$').strip(',')))
                                book['buy_used'] = new_prices[0]
                                book['buy_new'] = new_prices[1]
                                book['rent_used'] = new_prices[2]
                                book['rent_new'] = new_prices[3]
        collection.update_one(
            #{ '$unwind': '$campuses'},
            #{ '$unwind': '$campuses.terms'},
            {
            '_id': store['_id']
            },
            {'$set':{
                    'campuses':store['campuses']
                    }
            },
            upsert=False
        )

def add_unitid(client, db='test_db2'):
    """
    Adds IPEDS unitid to each store so other IPEDS data can be added to the correct stores.  Should update to add all IPEDS data in one function
    """
    collection = client[db].stores
    cursor = collection.find({'structure_complete':1,'books_complete':1},modifiers={"$snapshot": True})
    school_map = pickle.load(open('/Users/alexlevenstein/Documents/projects/books/BNcollege/Rewrite/info/mapped_schools.pkl','rb'))
    for store in cursor:
        collection.update_one(
            #{ '$unwind': '$campuses'},
            #{ '$unwind': '$campuses.terms'},
            {
            '_id': store['_id']
            },
            {'$set':{
                    'unitid':school_map[store['url']]
                    }
            },
            upsert=False
        )

def add_ipeds_data(client,db='test_db2'):
    all_schools_data = pd.read_csv('/Users/alexlevenstein/Documents/Galvanize/capstone/education_datasets/7-26-2016---812/Data_7-26-2016---812.csv')
    collection = client[db].stores
    cursor = collection.find({'structure_complete':1,'books_complete':1},modifiers={"$snapshot": True})
    for store in cursor:
        if store['unitid'] == 0:
            continue
        store_data = all_schools_data[all_schools_data['UnitID']==store['unitid']].values[0]
        #print len(store_data)

        collection.update_one(
            {
            '_id': store['_id']
            },
            {'$set':{
                    'type' : "Point",
                    'coordinates' : [store_data[4],store_data[5]],
                    'ug_enrollment' : int(store_data[3]),
                    'sfr' : store_data[2],
                    'zip' : store_data[6],
                    'state' : store_data[7]
                    }
            },
            upsert=False
        )

if __name__=='__main__':
    client = MongoClient()
    #categorize_terms(client,db='test_db3')
    #convert_book_data(client,db='test_db3')
    #add_unitid(client,db='test_db3')
    add_ipeds_data(client, db='test_db3')

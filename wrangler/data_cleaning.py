from pymongo import MongoClient

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
    rec_types = ['REQUIRED','REQUIRED PACKAGE','RECOMMENDED','RECOMMENDED PACKAGE','BOOKSTORE RECOMMENDED','PACKAGE COMPONENT','']
    for store in cursor:
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
                                if (not ''.join(prices)):
                                    continue
                                for purchase_type,price in zip(purchase_types,prices):
                                    if price == 'nan':
                                        new_prices.append(-1)
                                    else:
                                        new_prices.append(float(price.strip('$')))
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
def add_unitid(client):
    return 0
    
if __name__=='__main__':
    client = MongoClient()
    #categorize_terms(client,db='test_db2')
    #convert_book_data(client)

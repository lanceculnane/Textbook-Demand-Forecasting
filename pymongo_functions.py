from pymongo import MongoClient

def write_store_to_db(client, store, db = 'test_db'):
    if client[db].stores.find_one({'store_ID':store.ID},{'structure_complete':1}):
        client[db].stores.replace_one({'url':store.url},store.get_dict_repr())
    else:
        client[db].stores.insert_one(store.get_dict_repr())

def read_store_from_db(client,store, db = 'test_db'):
    return client[db].stores.find_one({'url':store.url})

def store_exists_in_db(client,store, db = 'test_db'):
    return bool(client[db].stores.find_one({"url":store.url},{'_id':0, 'structure_complete':1}))

def store_complete(client,store, db = 'test_db'):
    if store_exists_in_db(client,store):
        completion = client[db].stores.find_one({"url":store.url},{'_id':0, 'structure_complete':1,'books_complete':1})
        if (completion['structure_complete'] and completion['books_complete']):
            return True
    return False

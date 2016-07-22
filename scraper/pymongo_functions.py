from pymongo import MongoClient

def write_store_to_db(client, store, db = 'test_db'):
    """Writes bookstore to a mongo database, replaces current instance if it exists"""
    if client[db].stores.find_one({'store_ID':store.ID},{'structure_complete':1}):
        client[db].stores.replace_one({'url':store.url},store.get_dict_repr())
    else:
        client[db].stores.insert_one(store.get_dict_repr())

def read_store_from_db(client,store, db = 'test_db'):
    """Reads a store from the mongo database"""
    return client[db].stores.find_one({'url':store.url})

def store_exists_in_db(client,store, db = 'test_db'):
    """Returns True if store is already in database, False otherwise"""
    return bool(client[db].stores.find_one({"url":store.url},{'_id':0, 'structure_complete':1}))

def store_complete(client,store, db = 'test_db'):
    """Returns True if a store is complete (both structure and books), False otherwise"""
    if store_exists_in_db(client,store):
        completion = client[db].stores.find_one({"url":store.url},{'_id':0, 'structure_complete':1,'books_complete':1})
        if (completion['structure_complete'] and completion['books_complete']):
            return True
    return False

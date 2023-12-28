import pymongo
from Crypto.Hash import SHA512


class DB:
    def __init__(self, data_base_name='University_Server'):
        __connection_db = pymongo.MongoClient()
        self.__DB = __connection_db[data_base_name]

    def get_db_name(self):
        return self.__DB.name + 'DB'

    async def insert_new_user(self, name: str, password: str, role_name: str, public_key: str):
        user_itr = self.__DB['Users'].find({'name': name})
        if user_itr.count() != 0:
            for user in user_itr:
                if user['public_key'] == public_key:
                    return -1
        user = self.__DB['Users'].insert_one({
            'name': name,
            'password': password,
            'role_name':role_name,
            'public_key': public_key
        })
        return 1

    def query(self, collection_name, query):
        return self.__DB[collection_name].find(query)

    def check_user(self, name, public_key):
        return self.query('Users', {'public_key': public_key, 'name': name}).count() == 1

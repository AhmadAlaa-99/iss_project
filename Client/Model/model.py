import pymongo


class DB:
    def __init__(self, database_name='University_Client'):
        __connection_db = pymongo.MongoClient()
        self.__DB = __connection_db[database_name]

    def get_db_name(self):
        return self.__DB.name

    def insert_new_user(self, name: str,role_name:str, public_key: str):
        users = self.__DB['Users'].find({'name': name})
        if users.count() != 0:
            for user in users:
                if user['public_key'] == public_key:
                    return -1
        self.__DB['Users'].insert_one({
            'name': name,
             'role_name': role_name,
            'public_key': public_key
        })

    def query(self, collection_name, query):
        return self.__DB[collection_name].find(query)

    def get_users(self):
        return [user['name'] for user in self.query('Users', {})]
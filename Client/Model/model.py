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
                if user['UniqueKey'] == public_key or user['Name'] == name:
                    return -1
        self.__DB['Users'].insert_one({
             'name': name,
             'role_name': role_name,
             'UniqueKey': public_key
        })

    def query(self, collection_name, query):
        return self.__DB[collection_name].find(query)

    def get_users_name(self):
        return [user['name'] for user in self.query('Users', {})]

    def names_of_doctors(self):
        return [user['name'] for user in self.query('Users', {})]


    def get_public_key(self, username):
        res = self.query('Users', {
            'Name': username
        })
        return res[0]['PublicKey'] if res.count()==1 else None

    def get_private_key(self, username):
        res = self.query('Users', {
            'Name': username
        })
        return res[0]['PrivateKey'] if res.count()==1 else None
        


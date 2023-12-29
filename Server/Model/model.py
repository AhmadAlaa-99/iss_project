import pymongo

class DB:
    def __init__(self, data_base_name='UniversityServer'):
        __connection_db = pymongo.MongoClient()
        self.__DB = __connection_db[data_base_name]

    def get_db_name(self):
        return self.__DB.name + 'DB'

    def insert_new_user(self, name: str, password: str, public_key: str):
        user_itr = self.__DB['Users'].find({'Name': name})
        if user_itr.count() != 0:
            for user in user_itr:
                if user['PublicKey'] == public_key or user['Name'] == name:
                    return -1
        user = self.__DB['Users'].insert_one({
            'Name': name,
            'Password': password,
            'PublicKey': public_key
        })
        return 1

    def query(self, collection_name, query):
        return self.__DB[collection_name].find(query)

    def check_user(self, name, public_key):
        q_res = self.query('Users', {'PublicKey': public_key, 'Name': name})
        return [q_res[0], q_res.count() == 1]

    def add_active_user(self, user_name, public_key, peer):
        if not self.is_user_active(user_name):
            self.__DB['ActiveUsers'].insert_one({
                'user_name': user_name,
                'PublicKey': public_key,
                'Peer': peer
            })

    def remove_active_user(self, user_name, public_key):
        if self.is_user_active(user_name):
            self.__DB['ActiveUsers'].delete_one({
                'user_name': user_name,
                'PublicKey': public_key
            })

    def is_user_active(self, name):
        return self.query('ActiveUsers', {'Name': name}).count() == 1

    def get_user_by_peer(self, peer):
        return self.query('ActiveUsers', {"Peer": peer})






    def add_profile(self, user_name, phone_number, location, national_number):
        if self.is_user_active(user_name):
            self.__DB['Profile'].insert_one({
                'user_name': user_name,
                'phone_number': phone_number,
                'location': location,
                'national_number': national_number,
            })
            return 1
        return -1

    def add_project(self, doctor_name, student_name, subject_name, project_link,file):
     #   if self.is_user_active(student_name):
            self.__DB['Projects'].insert_one({
                'doctor_name': doctor_name,
                'student_name': student_name,
                'subject_name': subject_name,
                'project_link': project_link,
                'file': file,
            })
            return 1

    def add_mark(self, doctor_name, subject_name, file):
        self.__DB['Marks'].insert_one({
            'doctor_name': doctor_name,
            'subject_name': subject_name,
            'file': file,
        })
        return 1
    def names_of_doctor_students(self, student_name):
        return self.query('Projects', {'student_name': student_name})


    def get_user_elements(self, name):
        return self.query('Elements', {'Name': name})

    def get_element_by_title(self, name, title):
        if self.is_user_active(name):
            res = self.query('Elements', {'Name': name, 'Title': title})
        return res
        def get_profile(self,user_name):
         if self.is_user_active(user_name):
            res = self.query('Profile', {'user_name': user_name,'phone_number': phone_number,'location': location,'national_number': national_number})
        return res
        



    

    def update_element(self, name, old_title, title, password, description, files):
        res = self.get_element_by_title(name, old_title)
        if res is None or res.count() == 0:
            return -1
        else:
            self.__DB['Elements'].update_many({'Name': name, 'Title': old_title}, {'$set': {
                "Title": title,
                "Name": name,
                "Password": password,
                "Description": description,
                "Files": files
            }})
            return 1

    def delete_element(self, name, title):
        res = self.get_element_by_title(name, title)
        if res is None or res.count() == 0:
            return -1
        else:
            self.__DB['Elements'].delete_many({'Name': name, 'Title': title})
            return 1

    def get_user_password(self, name):
        res = self.is_user_active(name)
        if res == 1:
            return self.query('Users', {'Name': name})[0]['Password']
        else:
            return -1
    def get_user_national_number(self, name):
        res = self.is_user_active(name)
        if res == 1:
            return self.query('Profile', {'name': name})[0]['national_number']
        else:
            return -1
        

        def get_marks(self, subject_name):
            res = self.is_user_active(name)
            if res == 1:
                return self.query('Marks', {'subject_name': subject_name})[0]
            else:
                return -1



    def add_event(self, dic: dict):
        temp = {
            'Time': datetime.datetime.now().__str__()
        }
        for key, val in dic.items():
            temp[key] = val
        pubkey = self.get_user_publicKey(dic['Name'])
        temp['PublicKey'] = pubkey
        self.__DB['Events'].insert_one(temp)



    def get_projects(self, student_name):
        return self.query('Projects', {'student_name': student_name})


    def get_user_publicKey(self, user_name):
        res = self.query('Users', {'Name': user_name})
        return res[0]['PublicKey'] if res.count() == 1 else None
        
   


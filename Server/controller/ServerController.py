import asyncio
import json
import random
import socket as sk
import time
import Model.model as model
import Messages.Respond as Messages
class Server:
    def __init__(self,db_manager):
        self.__DB = model.DB()
        self.receive_buffer = 2048
        self.active_users = []
        db_manager.add_db(self.__DB)

    async def handle(self, address='127.0.0.1', port='50050'):
        print(self.__DB.get_db_name())
        self.main_sock = await asyncio.start_server(self.handle_conn, address, port, family=sk.AF_INET)
        try:
            async with self.main_sock:
                await self.main_sock.serve_forever()
        except Exception as e:
            await self.main_sock.wait_closed()
            self.main_sock.close()
            pass

    async def handle_conn(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.peer = writer.get_extra_info('peername')
        print(self.peer)
        try:
            while not writer.is_closing():
                data = await reader.read(self.receive_buffer)
                if not reader.at_eof():
                    results = self.handle_receive_message(data)
                    if results is not None:
                        for r in results:
                            writer.write(r)
                            await writer.drain()
                else:
                    break
            writer.close()
            await writer.wait_closed()
            print('Done ' + self.peer[0])
        except RuntimeError as r:
            usersItr = self.__DB.get_user_by_peer(writer.get_extra_info('peername'))
            for user in usersItr:
                self.__DB.remove_active_user(user['Name'], user['PublicKey'])
            print("Error")
        except ConnectionError as c:
            usersItr = self.__DB.get_user_by_peer(writer.get_extra_info('peername'))
            for user in usersItr:
                self.__DB.remove_active_user(user['Name'], user['PublicKey'])
            print("Connection Issue\t", self.peer[0])

    def handle_receive_message(self, mes: bytes):
        msg_str = mes.decode('utf8')
        try:
            msg_dict = json.loads(msg_str)
            if msg_dict['Type'] == 'Size':
                self.receive_buffer = int(msg_dict['Size'])
                return None
            elif msg_dict['Type'] == 'Empty':
                return None
            elif msg_dict['Type'] == 'NewUser':
                return self.__signup_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'OldUser':
                return self.__login_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'UpdateProfile':
                return self.__update_profile_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'SendProjects':
                return self.__send_projects_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'GetListMarks':
                return self.__get_marks_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'SendMarks':
                return self.__send_marks_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'GetListProjects':
                return self.__get_list_projects_handler(msg_dict=msg_dict)



        except Exception as e:
            print(e)
            print('Error in receive Message', msg_str)

    def __signup_handler(self, msg_dict):
        res = self.__DB.insert_new_user(msg_dict['Name'], msg_dict['Password'], msg_dict['UniqueKey'])
        if res == 1:
            self.__DB.add_active_user(msg_dict['Name'], msg_dict['UniqueKey'], self.peer)
            return [Messages.Respond.RespondMessage({'Type': 'Sign',
                                                     'Result': 'Done'
                                                     }).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'Sign',
                                                     'Result': 'Error In SignUp'
                                                     }).to_json_byte()]

    def __login_handler(self, msg_dict):
        query_res = self.__DB.check_user(msg_dict['Name'], msg_dict['UniqueKey'])
        if query_res[1]:
            if msg_dict['Password'] == query_res[0]['Password']:
                self.__DB.add_active_user(msg_dict['Name'], msg_dict['UniqueKey'], self.peer)
                return [Messages.Respond.RespondMessage({'Type': 'Login',
                                                         'Result': 'Done'
                                                         }).to_json_byte()]
            else:
                return [Messages.Respond.RespondMessage({'Type': 'Login',
                                                         'Result': 'Error In Login'
                                                         }).to_json_byte()]

    def __send_projects_handler(self, msg_dict):
        res = self.__DB.add_project(doctor_name=msg_dict['doctor_name'],
                                    student_name=msg_dict['student_name'],
                                    subject_name=msg_dict['subject_name'],
                                    project_link=msg_dict['project_link'],
                                    file=msg_dict['file'],
                                    )
        self.receive_buffer = 2048
        if res == 1:
            return [Messages.Respond.RespondMessage({'Type': 'SendProjects',
                                                     'Result': 'Done'
                                                     }).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'SendProjects',
                                                     'Result': 'Error In Projects Data'
                                                     }).to_json_byte()]

    def __update_profile_handler(self, msg_dict):
        res = self.__DB.add_profile(user_name=msg_dict['user_name'],
                                    phone_number=msg_dict['phone_number'],
                                    location=msg_dict['location'],
                                    national_number=msg_dict['national_number'],
                                    )
        self.receive_buffer = 2048
        if res == 1:
            return [Messages.Respond.RespondMessage({'Type': 'Put',
                                                     'Result': 'Done'
                                                     }).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'Put',
                                                     'Result': 'Error In Put Data'
                                                     }).to_json_byte()]

    def __get_marks_handler(self, msg_dict):
        res = self.__DB.get_marks(msg_dict['subject_name'])
        if res is not None:
            finalList = []
            if res.count() == 0:
                finalList.append(Messages.Respond.RespondMessage({'Type': 'GetListMarks',
                                                                  'Result': 'Error In GetListMarks'
                                                                  }).to_json_byte())
                return finalList
            else:
                temp_list = []
                for r in res:
                    get_mes = json.dumps({'subject_name': r['subject_name'],
                                          'file': r['file']
                                          })
                    temp_list.append(get_mes)
                    get_mes = Messages.Respond.RespondMessage(
                        {'Type': 'GetListMarks', 'Result': temp_list}).to_json_byte()
                    finalList.append(Messages.Respond.RespondMessage({'Type': 'GetListMarks',
                                                                      'Result': 'Done',
                                                                      'Size': 10 * len(get_mes)}).to_json_byte())
            finalList.append(get_mes)
        return finalList

    def __send_marks_handler(self, msg_dict):
        res = self.__DB.add_mark(doctor_name=msg_dict['doctor_name'],
                                 subject_name=msg_dict['subject_name'],
                                 file=msg_dict['file'],
                                 )
        self.receive_buffer = 2048
        if res == 1:
            return [Messages.Respond.RespondMessage({'Type': 'SendMarks',
                                                     'Result': 'Done'
                                                     }).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'SendMarks',
                                                     'Result': 'Error In SendMarks Data'
                                                     }).to_json_byte()]

    def __get_list_projects_handler(self, msg_dict):
        res = self.__DB.get_projects(msg_dict['student_name'])
        if res is not None:
            finalList = []
            if res.count() == 0:
                finalList.append(Messages.Respond.RespondMessage({'Type': 'GetListProjects',
                                                                  'Result': 'Error In GetListProjects'
                                                                  }).to_json_byte())
                return finalList
            else:
                temp_list = []
                for r in res:
                    get_mes = json.dumps({'doctor_name': r['doctor_name'],
                                          'student_name': r['student_name'],
                                          'subject_name': r['subject_name'],
                                          'project_link': r['project_link'],
                                          'file': r['file']
                                          })
                    temp_list.append(get_mes)
            get_mes = Messages.Respond.RespondMessage({'Type': 'GetListProjects', 'Result': temp_list}).to_json_byte()
            finalList.append(Messages.Respond.RespondMessage({'Type': 'GetListProjects',
                                                              'Result': 'Done',
                                                              'Size': 10 * len(get_mes)}).to_json_byte())
            finalList.append(get_mes)
            return finalList

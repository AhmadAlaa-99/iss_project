import asyncio
import json
import random
import socket as sk
import time
from base64 import b64decode
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import Model.model as model
import Messages.Respond as Messages
from Cryptography import SymmetricLayer as sl
class Server:
    def __init__(self,db_manager):
        self.__DB = model.DB()
        self.receive_buffer = 2048
        self.active_users = []
        db_manager.add_db(self.__DB)
        self.asl = asl.AsymmetricLayer()

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
        try:
            # Send Public Key To User
            if await self.init_authentication(reader, writer):
                # Send And Receive Processes
                while not writer.is_closing():
                    data = await reader.read(self.receive_buffer)
                    if not reader.at_eof():
                        # Comment's Lines Below are for Symmetric Encryption and Decryption
                        results = self.symmetric_send_encrypt(
                            self.handle_receive_message(
                                self.symmetric_receive_decrypt(data)))
                        # results = self.handle_receive_message(data)
                        if results is not None:
                            for r in results:
                                writer.write(r)
                                await writer.drain()
                    else:
                        break
                writer.close()
                await writer.wait_closed()
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

    async def init_authentication(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            writer.write(Messages.Configration.ConfigMessage(
                public_key=self.asl.rsa_pair.public_key()
                    .export_key().decode('utf8'))
                         .to_json_byte())
            await writer.drain()
            data = await reader.read(self.receive_buffer)
            mes_dic = json.loads(data)
            if mes_dic['Type'] == 'Session':
                self.session_key = self.asl.decrypt_config(mes_dic)
                if self.session_key is not False:
                    writer.write(Messages.Respond.RespondMessage(details={
                        'Type': 'Config',
                        'Result': 'Done'
                    }).to_json_byte())
                    await writer.drain()
                    return True
                else:
                    writer.write(Messages.Respond.RespondMessage(details={
                        'Type': 'Config',
                        'Result': 'Error'
                    }).to_json_byte())
                    await writer.drain()
                    return False
        except Exception as e:
            print('Init Authentication Error')


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
            elif msg_dict['Type'] == 'GetProfile':
                return self.__get_profile_handler(msg_dict=msg_dict)



        except Exception as e:
            print(e)
            print('Error in receive Message', msg_str)

    def __signup_handler(self, msg_dict):
        res = self.__DB.insert_new_user(msg_dict['Name'], msg_dict['Password'], msg_dict['UniqueKey'])
        if res == 1:
            self.__DB.add_active_user(msg_dict['Name'], msg_dict['PublicKey'], self.peer)
            return [Messages.Respond.RespondMessage({'Type': 'Sign',
                                                     'Result': 'Done'
                                                     }).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'Sign',
                                                     'Result': 'Error In SignUp'
                                                     }).to_json_byte()]

    def __login_handler(self, msg_dict):
        query_res = self.__DB.check_user(msg_dict['Name'], msg_dict['PublicKey'])
        if query_res[1]:
            if msg_dict['Password'] == query_res[0]['Password']:
                self.__DB.add_active_user(msg_dict['Name'], msg_dict['PublicKey'], self.peer)
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

    def __get_profile_handler(self, msg_dict):
        res = self.__DB.get_profile(msg_dict['user_name'])
        if res is not None:
            finalList = []
            if res.count() == 0:
                finalList.append(Messages.Respond.RespondMessage({'Type': 'GetProfile',
                                                                  'Result': 'Error In GetListMarks'
                                                                  }).to_json_byte())
                return finalList
            else:
                temp_list = []
                for r in res:
                    get_mes = json.dumps({'user_name': r['user_name'],
                                          'phone_number': r['phone_number'],
                                           'location': r['location'],
                                           'national_number' : r['national_number']
                                          })
                    temp_list.append(get_mes)
                    get_mes = Messages.Respond.RespondMessage(
                        {'Type': 'GetProfile', 'Result': temp_list}).to_json_byte()
                    finalList.append(Messages.Respond.RespondMessage({'Type': 'GetProfile',
                                                                      'Result': 'Done',
                                                                      'Size': 10 * len(get_mes)}).to_json_byte())
            finalList.append(get_mes)
        return finalList

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
    
    def symmetric_receive_decrypt(self, data: bytes):
        try:
            temp_dict = json.loads(data)
            public_key = self.__DB.get_user_publicKey(temp_dict['Name'])
            dec_dic = sl.SymmetricLayer(key=self.session_key).dec_dict(data,public_key)
            self.__DB.add_event(temp_dict)
            return dec_dic
        except Exception as e:
            print(e)
            print('Symmetric Receive Decrypt Error')

    def symmetric_send_encrypt(self, data):
        if data is None:
            return None
        else:
            enc_list = []
            sym_enc = sl.SymmetricLayer(key=self.session_key)
            for d in data:
                enc_list.append(sym_enc.enc_dict(d))
            return enc_list

        if data is None:
            return None
        else:
            enc_list = []
            national_number = self.__DB.get_user_national_number(self.last_user)
            if national_number != -1:
                key = 4 * national_number
                key = key[:32].encode('utf8')
                sym_enc = sl.SymmetricLayer(key=key)
                for d in data:
                    enc_list.append(sym_enc.enc_dict(d))
                return enc_list
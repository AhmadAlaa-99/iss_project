import os
import pathlib
import sys
import pathlib
import Messages.NewUser
import Messages.OldUser
import Model.Model as model
import Messages.GetListMarks
import Messages.GetListProjects
import Messages.SendMarks
import Messages.SendProjects
import base64
class CMDInput:

    def __init__(self,public_key=None):
        self.last_message = {}
        self.__DB = model.DB()
        self.user_name = None
        self.role_name = None
        self.public_key = public_key

    def init_input_ui(self):
        try:
            input_str = input("<<Welcome To Damascus University Server>>\n"
                              + "1.SignUp\n" + "2.Login\n"
                              + "3.exit\n" + "Choose: ").lower()
            if input_str in ['signup', '1']:
                self.__signup_ui()
            elif input_str in ['login', '2']:
                self.__login_ui()
            else:
                sys.exit(0)
        except Exception as e:
            print(e)

    def __signup_ui(self):
        try:
            user_name = input('user name: ')
            password = input('Password: ')
            while len(password) < 8:
                password = input('At Lest 8\nPassword: ')
            role_name = input('Choose role (student/doctor): ')
            while role_name not in ['student', 'doctor']:
               role_name = input('Invalid role. Choose either student or doctor: ')
            ms = Messages.NewUser.NewUserMessage(user_name=user_name,
                                                 password=password,
                                                 role_name=role_name,
                                                 )
            self.last_message = ms.to_json_string()
            self.user_name = user_name
            self.role_name = role_name
        except Exception:
            sys.exit(-1)

    def __login_ui(self):
        users_name = self.__DB.get_users_name()
        if len(users_name) != 0:
            print('<<Registered Users>>')
            for i, name in enumerate(users_name):
                print(i, name)
        try:
            user_name = input('Name: ')
            if user_name in users_name:
                password = input('Password: ')
                while len(password) < 8:
                    password = input('At Lest 8\nPassword: ')
                user = self.__DB.query('Users', {'Name': user_name})
                user_data = user[0]
                role_name = user_data.get('role_name')
                ms = Messages.OldUser.OldUserMessage(user_name=user_name,
                                                     password=password,
                                                     unique_key=user[0]['PublicKey'])
                self.last_message = ms.to_json_string()
                self.user_name = user_name
                self.role_name = role_name
                print (self.role_name)
            else:
                self.last_message = {
                    "Type": "Error",
                    "Description": "There No Such a User Name"
                }
        except Exception as e:
            print(e)
            sys.exit(-1)

    def operations_ui(self):
        try:
            if self.role_name is None:
                print("Role name is not available.")
                return

            if self.role_name.lower() == 'student':
                input_str = input("<<Student Operations UI>>\n"
                                  + "1.Update Profile\n2.Send Projects\n3.Browse Marks\n4.Profile\n5.Exit\n"
                                  + "Choose: ").lower()
                if input_str in ['Update_Profile', '1']:
                    self.__update_profile_ui()
                elif input_str in ['Send_Project', '2']:
                    self.__send_projects_ui()
                elif input_str in ['Browse Marks', '3']:
                    self.__browse_marks_ui()
                elif input_str in ['Browse Profile', '4']:
                    self.__browse_profile_ui()
                else:
                    sys.exit(0)
            elif self.role_name.lower() == 'doctor':
                input_str = input("<<Doctor Operations UI>>\n"
                                  + "1.Update Profile\n2.Send Marks\n3.Browse Projects\n4.Profile\n5.Exit\n"
                                  + "Choose: ").lower()
                if input_str in ['Update_Profile', '1']:
                    self.__update_profile_ui()
                elif input_str in ['Send Marks', '2']:
                    self.__send_marks_ui()
                elif input_str in ['Browse Projects', '3']:
                    self.__browse_projects_ui()
                elif input_str in ['Browse Profile', '4']:
                    self.__browse_profile_ui()
                else:
                    sys.exit(0)
            else:
                print("Unknown role")
                return
        except Exception as e:
            print(e)

    def __update_profile_ui(self):
        name = self.user_name
        if name is None:
            self.last_message = {
                "Type": "Error",
                "Description": "Not Signed Up Or Logged In!!"
            }
            return
        phone_number = input('phone_number: ')
        location = input('location: ')
        national_number = input('national_number: ')
        ms = Messages.UpdateProfile.UpdateProfile(phone_number=phone_number,
                                           location=location,
                                           name=name,
                                           national_number=national_number,
                                           )
        self.last_message = ms.to_json_string()

    def __send_projects_ui(self):
        names_of_doctors = self.__DB.names_of_doctors()
        if len(names_of_doctors) != 0:
            print('<<Names of doctors>>')
            for i, name in enumerate(names_of_doctors):
                print(i, name)
        try:
            doctor_name = input('Name: ')
            if doctor_name in names_of_doctors:
                subject_name = input('subject_name: ')
                project_link = input('project_link: ')
                file_path = input('To add a File, just type in the path of the File: ')
                files = {}
                # التحقق من أن المسار ليس فارغًا
                if file_path:
                    # إزالة علامات الاقتباس إذا كانت موجودة
                    if file_path[0] == '"' and file_path[-1] == '"':
                        file_path = file_path[1:-1]
                    # التحقق من وجود الملف
                    if pathlib.Path.exists(pathlib.Path(file_path)):
                        # التحقق من أن الملف هو ملف نصي
                        if file_path.split('\\')[-1].split('.')[-1] == 'txt':
                            with open(file_path, 'r+', encoding='utf8') as file:
                                files['1'] = {
                                    'FileName': file_path.split('\\')[-1],
                                    'File': file.read()
                                }
                        else:
                            print('Only supports txt file for now.')
                    else:
                        print('File does not exist.')
                else:
                    print('No file path provided.')
                ms = Messages.SendProjects.SendProjects(doctor_name=doctor_name,
                                                          student_name=self.user_name,
                                                          subject_name=subject_name,
                                                          project_link=project_link,
                                                          file=file,
                                                          )
                self.last_message = ms.to_json_string()
                print (self.role_name)
            else:
                self.last_message = {
                    "Type": "Error",
                    "Description": "There No Such a User Name"
                }
        except Exception as e:
            print(e)
            sys.exit(-1)

    def __browse_marks_ui(self):
        names_of_subjects = self.__DB.names_of_subjects()
        if len(names_of_subjects) != 0:
            print('<<Names of doctors>>')
            for i, name in enumerate(names_of_subjects):
                print(i, name)
        try:
            subject_name = input('subject_name: ')
            if subject_name in names_of_subjects:
                ms = Messages.GetListMarks.GetListMarks(subject_name=subject_name)
                self.last_message = ms.to_json_string()
            else:
                self.last_message = {
                    "Type": "Error",
                    "Description": "There No Such a User Name"
                }
        except Exception as e:
            print(e)
            sys.exit(-1)

            
    def __browse_profile_ui(self):
          try:
                ms = Messages.GetProfile.GetProfile(user_name=self.user_name)
                self.last_message = ms.to_json_string()
          except Exception as e:
              print(e)
              sys.exit(-1)

    def __send_marks_ui(self):
        try:
                subject_name = input('subject_name: ')
                file_path = input('To add a File, just type in the path of the File: ')
                files = {}
                # التحقق من أن المسار ليس فارغًا
                if file_path:
                    # إزالة علامات الاقتباس إذا كانت موجودة
                    if file_path[0] == '"' and file_path[-1] == '"':
                        file_path = file_path[1:-1]
                    # التحقق من وجود الملف
                    if pathlib.Path.exists(pathlib.Path(file_path)):
                        # التحقق من أن الملف هو ملف نصي
                        if file_path.split('\\')[-1].split('.')[-1] == 'txt':
                            with open(file_path, 'r+', encoding='utf8') as file:
                                files['1'] = {
                                    'FileName': file_path.split('\\')[-1],
                                    'File': file.read()
                                }
                        else:
                            print('Only supports txt file for now.')
                    else:
                        print('File does not exist.')
                else:
                    print('No file path provided.')
                ms = Messages.SendMarks.SendMarks(doctor_name=self.user_name,
                                                        subject_name=subject_name,
                                                        file=file,
                                                        )
                self.last_message = ms.to_json_string()
                print(self.role_name)

        except Exception as e:
            print(e)
            sys.exit(-1)
    def __browse_projects_ui(self):
        names_of_doctor_students = self.__DB.names_of_doctor_students()
        if len(names_of_doctor_students) != 0:
            print('<<Names of Students>>')
            for i, name in enumerate(names_of_doctor_students):
                print(i, name)
        try:
            student_name = input('student_name: ')
            if student_name in names_of_doctor_students:
                ms = Messages.GetListProjects.GetListProjects(student_name=student_name)
                self.last_message = ms.to_json_string()
            else:
                self.last_message = {
                    "Type": "Error",
                    "Description": "There No Such a User Name"
                }
        except Exception as e:
            print(e)
            sys.exit(-1)
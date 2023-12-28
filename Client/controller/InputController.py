from Messages import *
import Model.Model as model


class CMDInput:
    def __init__(self):
        self.Loged = False
        self.last_message = {}
        self.__DB = model.DB()
        self.role_name = None

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

    def signup_ui(self):
        print('signup')
        
    def login_ui(self):
        print('login')

    def operations_ui(self):
        try:
            if self.role_name is None:
                print("Role name is not available.")
                return

            # Now it's safe to use .lower() as role_name is not None
            if self.role_name.lower() == 'student':
                input_str = input("<<Student Operations UI>>\n"
                                  + "1.Update Information\n2.Submit Assignments\n3.Exit\n"
                                  + "Choose: ").lower()
            elif self.role_name.lower() == 'doctor':
                input_str = input("<<Doctor Operations UI>>\n"
                                  + "1.Update Information\n2.Review Projects\n3.Exit\n"
                                  + "Choose: ").lower()
            else:
                print("Unknown role")
                return
            if input_str in ['Update', '1']:
                self.__update_password_ui()
            elif input_str in ['Send', '2']:
                self.__put_Information_ui()
            else:
                sys.exit(0)
        except Exception as e:
            print(e)


    def put_password_ui(self):
        print('New Password')

    def get_password_ui(self):
        print('Get Password')

    def update_password_ui(self):
        print('Update Password')

    def delete_password_ui(self):
        print('Delete Password')

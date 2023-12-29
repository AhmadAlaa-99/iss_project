from Messages import Message as Ms


class GetProfile(Ms.Message):
    def __init__(self, user_name: str, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "GetProfile",
                    "user_name": user_name
                }
            elif message["Type"] == "GetProfile":
                super(GetProfile, self).__init__(message=message)
        except Exception as e:
            print(e)

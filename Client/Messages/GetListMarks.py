from Messages import Message as Ms


class GetListMarks(Ms.Message):
    def __init__(self, subject_name: str, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "GetListMarks",
                    "subject_name": subject_name
                }
            elif message["Type"] == "GetListMarks":
                super(GetListMarks, self).__init__(message=message)
        except Exception as e:
            print(e)

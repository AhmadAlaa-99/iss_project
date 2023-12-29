from Messages import Message as Ms


class GetListProjects(Ms.Message):
    def __init__(self, student_name: str, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "GetListProjects",
                    "student_name": student_name
                }
            elif message["Type"] == "GetListProjects":
                super(GetListProjects, self).__init__(message=message)
        except Exception as e:
            print(e)

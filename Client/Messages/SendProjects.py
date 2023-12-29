from Messages import Message as Ms


class SendProjects(Ms.Message):
    def __init__(self,doctor_name: str,student_name: str,subject_name: str,project_link: str, file: dict, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "SendProjects",
                    "doctor_name": doctor_name,
                    "student_name": student_name,
                    "subject_name": subject_name,
                    "project_link": project_link,
                    "file": file
                }
            elif message['Type'] == "SendProjects":
                super(SendProjects, self).__init__(message=message)
        except Exception as e:
            print(e)

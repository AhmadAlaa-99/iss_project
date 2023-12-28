from Messages import Message as Ms


class SendProjects(Ms.Message):
    def __init__(self,name: str, description: str, files: dict, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "SP",
                    "Name": name,
                    "Description": description,
                    "Files": files
                }
            elif message['Type'] == "SP":
                super(SendProjects, self).__init__(message=message)
        except Exception as e:
            print(e)

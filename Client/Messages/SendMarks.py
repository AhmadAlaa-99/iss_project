from Messages import Message as Ms
class SendMarks(Ms.Message):
    def __init__(self,name: str, mark: str,message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "SM",
                    "name": name,
                    "mark": mark,
                }
            elif message['Type'] == "SM":
                super(SendMarks, self).__init__(message=message)
        except Exception as e:
            print(e)

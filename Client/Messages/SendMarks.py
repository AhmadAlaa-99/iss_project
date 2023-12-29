from Messages import Message as Ms
class SendMarks(Ms.Message):
    def __init__(self,doctor_name: str, subject_name: str,file: dict,message: dict = None):
        try:

            if message is None:
                self.message_info = {
                    "Type": "SendMarks",
                    "doctor_name": doctor_name,
                    "subject_name": subject_name,
                    "file": file,
                }
            elif message['Type'] == "SendMarks":
                super(SendMarks, self).__init__(message=message)
        except Exception as e:
            print(e)

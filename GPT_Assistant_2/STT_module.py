
import requests
from Utility import AudioFile
from abc import ABC, abstractmethod
from Logger import Logger

class SttInterface(ABC):

    url=""
    token=""

    @abstractmethod
    def recognize(self, AudioFile):
        pass

    @abstractmethod
    def recognize_from_file(self, FilePath):
        pass


class OpenAiStt(SttInterface):
    """
    Реализация TTS api OpenAi
    """

    def __init__(self, URL="", TOKEN=""):
        self.allowed_input_formats = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm","ogg"]
        self.__model = "whisper-1"
        SttInterface.url=URL
        SttInterface.token=TOKEN
        self.__headers = {
            "Authorization": f"Bearer {self.token}"
        }

    @staticmethod
    @Logger.log_call
    def is_allowed(value, list_of_allowed_values):
        """
        Проверяет допустимость значения по списку допустимых значений
        :param value: Значение подлежащее проверке
        :param list_of_allowed_values: Список допустимых значений
        :return: True || False
        """
        return value.lower() in list_of_allowed_values

    @Logger.log_call
    def recognize(self, input_file):
        try:
            #if input_file.extension not in self.allowed_input_formats:
                #return None
            req_body={
                "model": self.__model,
                "response_format": "text"
            }
            response = requests.post(
                self.url,
                headers=self.__headers,
                data=req_body,
                files={"file": (input_file.name, input_file.body, "audio/" + input_file.extension)}
            )
            if response.status_code != 200:
                return None
            return response.text
        except Exception as e:
            print(f"В процессе распознования речи произошла ошибка: {e}")

    @Logger.log_call
    def recognize_from_file(self, FilePath):
        try:
            audio=AudioFile.from_path(FilePath)
            with open(FilePath, "rb") as os_file:
                audio.body=os_file.read()
            if audio.extension not in self.allowed_input_formats or audio.body is None:
                return None
            result_string = self.recognize(audio)
            return result_string
        except Exception as e:
            print(f"Ошибка STT: {e}")
            return None


if __name__ == "__main__":
    stt=OpenAiStt("URL","TOKEN")
    print(stt.recognize_from_file("329564358_469160066.ogg"))
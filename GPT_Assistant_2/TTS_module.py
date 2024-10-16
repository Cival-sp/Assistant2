import requests
from abc import ABC, abstractmethod
import random
import string


class AudioFile:
    def __init__(self, FileName, FileExtension, Body=None):
        self.fileName = FileName
        self.fileExtension = FileExtension
        self.body = Body


class TtsInterface(ABC):

    @abstractmethod
    def to_voice(self, text):
        """
        Озвучивает переданный текст в соотвествии с параметрами обьекта класса
        :param text: Текст для озвучивания
        :return: AudioFile
        """
        pass


class OpenAiTTS(TtsInterface):
    """
    Реализация TTS api OpenAi
    """

    def __init__(self, URL="", TOKEN=""):
        self.allowed_models = ["tts-1", "tts-1-hd", "whisper-1"]
        self.allowed_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.allowed_output_formats = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
        self.allowed_input_formats = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
        self.url = URL
        self.token = TOKEN
        self.speed = 1.0

        self.__voice = "nova"
        self.__model = "tts-1"
        self.__output_format = "wav"
        self.__headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def is_allowed(value, list_of_allowed_values):
        """
        Проверяет допустимость значения по списку допустимых значений
        :param value: Значение подлежащее проверке
        :param list_of_allowed_values: Список допустимых значений
        :return: True || False
        """
        return value.lower() in list_of_allowed_values

    @staticmethod
    def generate_random_filename(length: int) -> str:
        """
        Генерирует случайное название файла заданной длины без расширения.

        :param length: Длина названия файла.
        :return: Сгенерированное случайное название файла.
        """
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return random_chars

    def set_model(self, model):
        if model in self.allowed_models:
            self.__model = model
            return True
        else:
            return False

    def set_voice(self, voice):
        if voice in self.allowed_voices:
            self.__voice = voice
            return True
        else:
            return False

    def set_output_format(self, output_format):
        if output_format in self.allowed_output_formats:
            self.__output_format = output_format
            return True
        else:
            return False

    def get_model(self):
        return self.__model

    def get_voice(self):
        return self.__voice

    def get_output_format(self):
        return self.__output_format

    def create_json(self):
        jsn = {
            "model": self.__model,
            "voice": self.__voice,
            "response_format": self.__output_format,
            "speed": self.speed,
        }
        return jsn

    def to_voice(self, text):
        """
        Метод для озвучивания переданного в метод текста. При генерации аудио, используются параметры обьекта.
        :param text: Текст для озвучивания.
        :return: Возвращает обьект класса AudioFile или None
        """
        try:
            request_json = self.create_json()
            request_json["input"] = text
            response = requests.post(self.url, json=request_json, headers=self.__headers)
            if response.status_code != 200:
                return None
            result_audio_file = AudioFile(OpenAiTTS.generate_random_filename(16), "." + self.__output_format,
                                          response.content)
            return result_audio_file
        except Exception as e:
            print(f"В процессе запроса к серверу TTS произошла ошибка: {e}")
            return None


if __name__ == "__main__":
    tts = OpenAiTTS("https://api.proxyapi.ru/openai/v1/audio/speech", "sk-cmsdlCHR3YhviLU2UJcspxAfiDJfynmr")
    tts.set_model("tts-1")
    tts.set_voice("nova")
    tts.speed = 0.9
    file = tts.to_voice("Это образец синтеза речи через OpenAi api")
    with open(file.fileName+file.fileExtension, "wb") as f:
        f.write(file.body)

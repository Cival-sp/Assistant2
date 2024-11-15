import requests
import json
from abc import ABC, abstractmethod

from flask import request

from Logger import Logger

class GptInterface(ABC):
    """Интерфейс для работы с GPT """


    @abstractmethod
    def __init__(self):
        self.url = None
        self.token = None
        pass

    @abstractmethod
    def ask(self, message, python_json_pattern=None):
        """
        :param message: Текущее сообщение которое будет отправлено GPT.
        :param python_json_pattern: Json шаблон, может быть использован для задания промта или истории сообщений.
        :return : Возвращает строку с ответом GPT.
        """
        pass

    @abstractmethod
    def send_json(self, json_dict):
        """
        Отправляет GPT модели кастомный json, используя заданную модель при инициализации
        :param json_dict: словарь, который будет преобразован в json и отправлен модели.
        :return: Возвращает json или None
        """
        pass


class OpenAiGPT(GptInterface):
    """
    Реализация api chatGPT
    """

    def __init__(self):
        self.allowed_models = ["gpt-4o-mini", "gpt-4o", "o1-mini", "o1-preview", "gpt-3.5-turbo"]
        self.model = "gpt-4o-mini"
        self.token=None
        self.url=None
        self.headers = {
            "Authorization": f"Bearer {OpenAiGPT.token}",
            "Content-Type": "application/json"
        }

    @Logger.log_call
    def is_allowed_model(self, model):
        model = model.lower()
        if model in self.allowed_models:
            return True
        else:
            return False

    @Logger.log_call
    def create_default_json(self, prompt=None):
        json_data = {
            "model": self.model,
            "messages": []
        }
        if prompt is not None:
            json_data["messages"].append({
                "role": "system",
                "content": prompt
            })
        return json_data


    @staticmethod
    @Logger.log_call
    def extract_string_from_answer(response):
        if response.status_code != 200:
            return None
        else:
            response_json = response.json()
            gpt_message = response_json['choices'][0]['message']['content']
            return gpt_message

    @Logger.log_call
    def set_model(self, model):
        if self.is_allowed_model(model):
            self.model = model
            return True
        else:
            return False

    @Logger.log_call
    def ask(self, message, json_pattern=None, prompt=None):
        """
        Отправляет сообщение GPT модели. При необходимости можно передать словарь с историей или промтом.
        :param message: Сообщение от пользователя
        :param json_pattern: Словарь-шаблон |Опционально
        :param prompt: Промт для chatGPT от имени системы |Опционально
        :return: Строка. Ответ от модели. || None
        """
        try:
            if json_pattern is None:
                json_pattern = self.create_default_json(prompt)

            json_pattern['messages'].append({
                "role": "user",
                "content": message
            })
            response = requests.post(self.url, json=json_pattern, headers=self.headers)
            gpt_answer = OpenAiGPT.extract_string_from_answer(response)
            if gpt_answer is not None:
                return gpt_answer
            else:
                return None
        except Exception as e:
            print(e)
            return None

    @Logger.log_call
    def send_json(self, json_dict):
        try:
            to_send_json = {
                "model": self.model,
            }
            to_send_json.update(json_dict)
            response = requests.post(self.url, json=to_send_json, headers=self.headers)
            if response.status_code != 200:
                print(f"Запрос {request}, ответ: {response.json()}")
                raise Exception(f"Ответ сервера GPT: {response.status_code}")
                return None
            res_json = response.json()
            if res_json is not None:
                return res_json
            else:
                return None
        except Exception as e:
            print(f"В процессе запроса к серверу GPT произошла ошибка: {e}")
            return None


if __name__ == "__main__":
    OpenAiGPT.token = "<KEY>"
    OpenAiGPT.url = "host"
    gpt4_mini = OpenAiGPT()
    j = {
        "messages": [
            {
                "role": "system",
                "content": """
                Текст для пользователя помести по ключу "text"
                Для выполнения команды помести ее в массив "commands"
                Для продолжения беседы или получения результатов выполнения команды используй флаг "continue_dialog"
                """

            },
            {
                "role": "user",
                "content": "Какая погода сегодня в москве ?"
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "text": "",
                "commands": [],
                "continue_dialog": False
            },
            "strict": True
        }
    }
    print(j)
    res=gpt4_mini.send_json(j)
    print( json.dumps(res, indent=4) )

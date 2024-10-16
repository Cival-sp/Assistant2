import requests
from abc import ABC, abstractmethod


class GptInterface(ABC):
    """Интерфейс для работы с GPT """

    @abstractmethod
    def __init__(self, url="", token=""):
        """
        :param url: URL для запроса к api GPT
        :param token: Token авторизации api GPT
        """
        self.url = url
        self.token = token
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
        :param json_dict: словарь, который будет преобразован в json и отправлен модели
        :return: Возвращает строку или None
        """
        pass


class OpenAiGPT(GptInterface):
    """
    Реализация api chatGPT
    """

    def __init__(self, url="", token=""):
        self.allowed_models = ["gpt-4o-mini", "gpt-4o"]
        self.url = url
        self.token = token
        self.__model = "gpt-4o-mini"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def is_allowed_model(self, model):
        model = model.lower()
        if model in self.allowed_models:
            return True
        else:
            return False

    def create_default_json(self, prompt=None):
        json_data = {
            "model": self.__model,
            "messages": []
        }
        if prompt is not None:
            json_data["messages"].append({
                "role": "system",
                "content": prompt
            })
        return json_data

    @staticmethod
    def extract_string_from_answer(response):
        if response.status_code != 200:
            return None
        else:
            response_json = response.json()
            gpt_message = response_json['choices'][0]['message']['content']
            return gpt_message

    def set_model(self, model):
        if self.is_allowed_model(model):
            self.__model = model
            return True
        else:
            return False

    def ask(self, message, json_pattern=None):
        """
        Отправляет сообщение GPT модели. При необходимости можно передать словарь с историей или промтом.
        :param message: Сообщение от пользователя
        :param json_pattern: Словарь-шаблон
        :return: Строка. Ответ от модели. || None
        """
        try:
            if json_pattern is None:
                json_pattern = self.create_default_json()

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

    def send_json(self, json_dict):
        try:
            to_send_json = {
                "model": self.__model,
            }
            to_send_json.update(json_dict)
            response = requests.post(self.url, json=to_send_json, headers=self.headers)
            res_str = OpenAiGPT.extract_string_from_answer(response)
            if res_str is not None:
                return res_str
            else:
                return None
        except Exception as e:
            print(e)
            return None


if __name__ == "__main__":
    gpt4_mini = OpenAiGPT("https://api.proxyapi.ru/openai/v1/chat/completions", "sk-cmsdlCHR3YhviLU2UJcspxAfiDJfynmr")
    # print(gpt4_mini.ask("Расскажи о себе, пожалуйста"))
    j = {
        "messages": [
            {
                "role": "system",
                "content": "Какие данные может возвращать chat gpt в json файле ответа? "
            }
        ]
    }
    print(gpt4_mini.send_json(j))

    print("end")

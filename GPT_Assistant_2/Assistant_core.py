from Utility import validate_json
from Command_processor import Command, CommandProcessor
import time


class AssistantRequest:
    def __init__(self):
        self.message = None
        self.is_audio_message = False
        self.file = None
        self.file_type = None


class AssistantAnswer:
    def __init__(self):
        self.text = None
        self.command = None
        self.continue_conversation = None
        self.prompt_tokens = None
        self.total_tokens = None
        self.gpt_tokens = None

    @staticmethod
    def from_json(json_dict):
        """
        Создает объект AssistantAnswer из словаря JSON.
        :param json_dict: Словарь JSON, содержащий данные для инициализации объекта.
        :return: Экземпляр AssistantAnswer.
        """
        json_dict = validate_json(json_dict)
        instance = AssistantAnswer()
        instance.text = json_dict.get("text")
        command_json = json_dict.get("command")
        if command_json:
            instance.command = Command.from_json(command_json)
        instance.continue_conversation = json_dict.get("continueConversation", False)

        return instance

    def to_json(self):
        """
        Преобразует объект AssistantAnswer в словарь JSON.
        :return: Словарь JSON, представляющий объект AssistantAnswer.
        """
        json_dict = {
            "Text": self.text,
            "continueConversation": self.continue_conversation
        }
        if self.command:
            json_dict["command"] = self.command.to_json()
        return json_dict


class Session:
    def __init__(self, user_id):
        self.user_id = user_id
        self.session_id = None
        self.last_call = time.time()
        self.history = []


class SessionManager:
    def __init__(self):
        self.current_session = None
        self.session_timeout = 20  # minutes
        self.history_max_len = 5
        self.session_history = []
        self.database = None

    def check_timeout(self):
        if self.current_session is not None:
            current_unix_time = time.time()
            if current_unix_time >= self.current_session.last_call + self.session_timeout * 60:
                self.session_history.append(self.current_session)
                self.current_session = None

    def clear_history(self):
        if self.database is not None:
            self.database.save_user_sessions(self.session_history)
        self.session_history.clear()

    def do(self):
        self.check_timeout()
        if len(self.session_history) >= self.history_max_len:
            self.clear_history()

    def find_user_session_in_db(self, user_id):  # use carefully
        if self.database is not None:
            return self.database.load_user_sessions(user_id)
        else:
            return None


class AssistantLogicCore:
    """
    Класс отвечающий за подготовку обращений к GPT api, обработку ответов, логику работы
    """

    def __init__(self, session, assistant_obj, database=None):
        self.user_id = session.user_id
        self.gpt_model = assistant_obj.gpt_model
        self.assistant_person = assistant_obj.assistant_person
        self.database = database
        self.command_processor = CommandProcessor()

    def prepare_message(self, role, message):
        res = AssistantRequest()
        return res

    def parse_answer(self, gpt_answer_json):
        answer_dict = validate_json(gpt_answer_json)
        result = AssistantAnswer()
        result.text = answer_dict["choices"][0]["content"]["Text"]
        result.command = Command.from_json(answer_dict["choices"][0]["content"]["command"])
        result.continue_conversation = answer_dict["choices"][0]["content"]["continueConversation"]
        result.total_tokens = answer_dict["total_tokens"]
        result.prompt_tokens = answer_dict["prompt_tokens"]
        result.gpt_tokens = result.total_tokens - result.prompt_tokens
        return result

from GPT_module import GptInterface, OpenAiGPT
from User_module import Assistant, Message, User
from Utility import validate_json, AudioFile, validate_data
from Command_processor import Command, CommandProcessor
import time
import threading
from Logger import Logger


class AssistantRequest:
    def __init__(self, message=None, user_id=None):
        self.message = message
        self.user_id = user_id
        self.user = None
        self.voice_data = None #AudioFile
        self.is_audio_message = False
        self.file = None
        self.file_type = None


class AssistantAnswer:
    def __init__(self):
        self.text = None
        self.command = None
        self.continue_conversation = None
        self.file = None
        self.file_type = None
        self.prompt_tokens = None
        self.total_tokens = None
        self.gpt_tokens = None
        self.request = None

    @staticmethod
    @Logger.log_call
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

    @Logger.log_call
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
    session_count = 0

    def __init__(self, user_id):
        self.user_id = user_id
        self.session_id = Session.session_count + 1
        self.last_call = time.time()
        self.history = []  # [Message]
        Session.session_count = self.session_id

    @Logger.log_call
    def update_call_time(self):
        self.last_call = time.time()

    @Logger.log_call
    def append(self, msg_arr):
        if isinstance(msg_arr, list) or isinstance(msg_arr, tuple):
            self.history.extend(msg_arr)
        if isinstance(msg_arr, Message):
            self.history.append(msg_arr)
        raise TypeError(f"в метод Session.append передан обьект класса{type(msg_arr)}")


class SessionManager:
    def __init__(self, timeout_min=60, max_len=1, database=None):
        self.current_sessions = {}  # Словарь для хранения сессий по user_id
        self.session_timeout = timeout_min * 60  # Время таймаута сессии в секундах
        self.history_max_len = max_len  # Максимальная длина истории
        self.database = database  # Подключение к базе данных, если нужно
        self.mutex = threading.Lock()  # Мьютекс

    def add_session(self, user_id):
        """Добавляет новую сессию для указанного user_id."""
        with self.mutex:
            if user_id not in self.current_sessions:
                self.current_sessions[user_id] = []  # Создаем список сессий для нового пользователя
            self.current_sessions[user_id].append(Session(user_id))  # Добавляем новую сессию

    def check_timeout(self):
        """Проверяет сессии на истечение времени."""
        with self.mutex:
            count = 0
            current_unix_time = time.time()  # Получаем текущее время
            expired_sessions = []  # Список для хранения устаревших сессий

            for user_id, session_array in list(self.current_sessions.items()):
                for session in session_array[:]:  # Создаем копию списка для безопасного удаления
                    if isinstance(session, Session):
                        if current_unix_time >= session.last_call + self.session_timeout:
                            expired_sessions.append(session)  # Добавляем сессию в список устаревших
                            session_array.remove(session)  # Удаляем устаревшую сессию
                            count += 1

                # Удаляем ключ из словаря, если не осталось сессий
                if not session_array:
                    del self.current_sessions[user_id]

            if self.database is not None:
                self.database.save_user_sessions(expired_sessions)  # Сохраняем устаревшие сессии в базе данных

            if count > 0:
                print(f"Очищено {count} устаревших сессий")  # Сообщаем о количестве очищенных сессий
        return count

    def clear_history(self, session):
        """Очищает историю сессии, если она превышает максимальную длину."""
        with self.mutex:
            if len(session.history) >= self.history_max_len:
                session.history = session.history[-self.history_max_len:]  # Оставляем только последние записи

    def update_last_call(self, user_id):
        """Обновляет время последнего вызова для активной сессии пользователя."""
        with self.mutex:
            if user_id in self.current_sessions:
                for session in self.current_sessions[user_id]:
                    if isinstance(session, Session):
                        session.last_call = time.time()
                        break

    @Logger.log_call
    def get_last_session(self, user_id):
        """Возвращает последнюю сессию для указанного user_id, если она существует."""
        with self.mutex:
            if user_id in self.current_sessions and self.current_sessions[user_id]:
                return self.current_sessions[user_id][-1]
            return None

    def active_sessions_count(self, user_id):
        """Возвращает количество активных сессий для указанного user_id."""
        with self.mutex:
            if user_id in self.current_sessions:
                return len(self.current_sessions[user_id])  # Возвращаем количество сессий для пользователя
            return 0

    def total_active_sessions(self):
        """Возвращает общее количество валидных активных сессий."""
        with self.mutex:
            total_count = 0
            for session_array in self.current_sessions.values():
                total_count += len(session_array)
            return total_count

    def do(self):
        """Выполняет периодическую проверку и очистку устаревших сессий."""
        with self.mutex:
            self.check_timeout()
            for sessions in self.current_sessions.values():
                for session in sessions:
                    self.clear_history(session)


class AssistantLogic:
    def __init__(self, command_processor: CommandProcessor, session_manager, stt_service, tts_service, database=None):
        self.command_processor = command_processor
        self.session_manager = session_manager
        self.stt_service = stt_service
        self.tts_service = tts_service
        self.database = database
        # Not init fields
        self.current_gpt_model = None
        self.current_assistant_person = None
        self.current_session = None
        self.current_user = None

    @Logger.log_call
    def init_session(self, user: User):
        self.current_user = user
        self.current_assistant_person = user.person_assistant
        self.current_gpt_model = user.person_assistant.model
        self.current_session = self.session_manager.get_last_session(user.user_id)
        if isinstance(self.current_session, Session):
            self.current_session.update_call_time()

    @Logger.log_call
    def close_session(self):
        self.current_user = None
        self.current_assistant_person = None
        self.current_gpt_model = None
        self.current_session = None

    @Logger.log_call
    def update_session(self, messages):
        if not isinstance(messages, list) or not isinstance(messages, tuple) or not isinstance(messages, Message):
            raise TypeError(f"update_session передан неподходящий тип {type(messages)}")
        if messages is None:
            raise TypeError(f"Передан None в update_session")
        self.current_session.append(messages)

    @Logger.log_call
    def fast_update_session(self, role: str, message: str) -> None:
        self.update_session(Message(role, message))

    @Logger.log_call
    def make_json_for_request(self, __request):
        if self.current_gpt_model is not None:
            if self.current_gpt_model.model is None:
                raise Exception("Некорректная GPT модель")
            res_json = {
                "model": self.current_gpt_model.model,
                "messages": [],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "assistant_response",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "Text": {
                                    "type": "string",
                                    "description": "Текст, который ассистент выводит пользователю. Может быть пустым, если вывод не требуется."
                                },
                                "command": {
                                    "type": "object",
                                    "description": "Команда, которую ассистент может отправить для выполнения, с произвольным числом параметров.",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "Название команды, которую нужно выполнить."
                                        },
                                        "parameters": {
                                            "type": "object",
                                            "description": "Произвольный набор параметров для выполнения команды.",
                                            "additionalProperties": {
                                                "type": "string",
                                                "description": "Значение параметра, которое может быть любого типа, представленное в виде строки."
                                            }
                                        }
                                    },
                                    "required": [
                                        "name"
                                    ]
                                },
                                "continueConversation": {
                                    "type": "boolean",
                                    "description": "Установи этот флаг, если требуется дополнительная информация от пользователя или если следует продолжить беседу"
                                }
                            },
                            "required": [
                                "continueConversation"
                            ],
                            "additionalProperties": False
                        }
                    }
                }
            }
            if __request.user_id is None:
                role = "system"
            else:
                role = "user"
            if self.current_session is not None:
                chat_history = self.current_session.history
                for message in chat_history:
                    res_json["messages"].append({"role": message.sender, "content": message.text})
            res_json["messages"].append({"role": role, "content": __request.message})
            return res_json
        raise Exception("GPT модель не задана или некорректна")

    @Logger.log_call
    def parse_answer(self, gpt_answer_json) -> AssistantAnswer:
        answer_dict = validate_json(gpt_answer_json)
        result = AssistantAnswer()
        result.text = answer_dict["choices"][0]["content"]["Text"]
        result.command = Command.from_json(answer_dict["choices"][0]["content"]["command"])
        result.continue_conversation = answer_dict["choices"][0]["content"]["continueConversation"]
        result.total_tokens = answer_dict["total_tokens"]
        result.prompt_tokens = answer_dict["prompt_tokens"]
        result.gpt_tokens = result.total_tokens - result.prompt_tokens
        return result

    @Logger.log_call
    def audio_preprocessing(self, request: AssistantRequest) -> bool:
        recognized_text = self.stt_service.recognize(request.voice_data)
        if recognized_text is None:
            raise Exception(f"Не распознан текст в запросе {request.user_id}")
        request.text = recognized_text
        # Сохранить при необходимости аудиофайл
        return True



    @Logger.log_call
    def text_processing(self, request: AssistantRequest) -> AssistantAnswer:
        validate_data(request, AssistantRequest)
        if not request.message:
            raise f"В запросе {request.user_id}  отсутствует текст для обработки"
        req_json = self.make_json_for_request(request)
        answer_json = self.current_gpt_model.send_json(req_json)
        answer_obj = self.parse_answer(answer_json)
        answer_obj.request = request
        # обновляем историю сообщений
        self.fast_update_session("user", request.message)
        self.fast_update_session("assistant", answer_obj.text)
        return answer_obj

    @Logger.log_call
    def analyze_command_result(self, cmd_res: str) -> str:
        req_json = self.make_json_for_request(AssistantRequest(cmd_res, None))
        gpt_result_json = self.current_gpt_model.send_json(req_json)
        if gpt_result_json is None:
            raise Exception("Нет ответа от gpt модели во время анализа результата выполнения команды")
        gpt_text = self.parse_answer(gpt_result_json).text
        return gpt_text

    @Logger.log_call
    def command_processing(self, command: Command) -> str:
        command_return = self.command_processor.execute_command(command)
        if command_return is None:
            raise Exception("Выполнение команды вернуло None")
        analyzed_text = self.analyze_command_result(command_return)
        self.current_session.append(Message("assistant", analyzed_text))
        return analyzed_text

    @Logger.log_call
    def is_voice(self,request: AssistantRequest) -> bool:
        if request.voice_data is not None:
            request.is_voice_message = True
            return True
        else:
            return False

    @Logger.log_call
    def process_session(self, request: AssistantRequest) -> AssistantAnswer or AudioFile:
        try:
            self.init_session(request.user)
            self.is_voice(request)
            if request.is_audio_message:
                self.audio_preprocessing(request)
            result = self.text_processing(request)
            if result.command is not None:
                result.text = self.command_processing(result.command)
            if request.is_audio_message:
                self.close_session()
                return self.tts_service.to_voice(result.text)
            self.close_session()
            return result
        except Exception as e:
            print(e)
        finally:
            self.close_session()

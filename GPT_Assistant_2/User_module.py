from enum import Enum
from GPT_Assistant_2.GPT_module import OpenAiGPT
import time
import threading
from Logger import Logger


class Message:
    def __init__(self, sender_name, text):
        self.send_unix_time = time.time()
        self.sender = sender_name
        self.text = text


class Person:
    class Gender(Enum):
        MALE = "Male"
        FEMALE = "Female"

    def __init__(self, name, last_name=None, age=None, gender=None):
        self.first_name = name
        self.last_name = last_name
        self.age = age if isinstance(age, int) else None
        self.gender = gender
        self.voice_sample = None
        self.photo_sample = None
        self.about = None


class Assistant:
    system_prompt = None

    def __init__(self):
        self.person = Person("Eve(Ева)")
        self.user_prompt = None
        self.model = OpenAiGPT()


class User:
    class Group(Enum):
        OWNER = "Владелец"
        ADMIN = "Администратор"
        VIP = "Привилегированный пользователь"
        COMMON = "Пользователь"
        GUEST = "Гость"
        BANNED = "Заблокирован"

    def __init__(self, user_id, user_login, user_name=None, user_group=None):
        self.user_id = user_id
        self.user_avatar = None
        self.user_group = user_group
        self.human_person = Person(user_name)
        self.person_assistant = Assistant()
        self.user_contacts = {
            "mobile_phone": None,
            "email": None
        }
        self.additional_info = {
            "token_used": 0,
            "last_seen": None
        }
        self.authorization_data = {
            "login": user_login,
            "password": "1",
        }
        self.settings = {}

        self.person_assistant.model.model = "gpt-4o-mini"
        self.person_assistant.model.token = ""
        self.person_assistant.model.url = ""


    @staticmethod
    @Logger.log_call
    def init_default_user(user_id):
        user = User(user_id, "Гость")
        user.user_avatar = None
        user.person_assistant.model.model="gpt-4o-mini"
        user.person_assistant.model.token = ""
        user.person_assistant.model.url = ""
        return user


class UserManager:
    _users = {
        1: User(1, "admin", User.Group.BANNED),
        2: User(2, "cival", User.Group.ADMIN)
    }
    _busy_logins = {"admin", "Cival"}
    _busy_id = set(_users.keys())
    _user_count = len(_users)
    _mutex = threading.Lock()

    @staticmethod
    def update_fields():
        with UserManager._mutex:
            UserManager._busy_id = set(UserManager._users.keys())
            UserManager._user_count = len(UserManager._users)

    @staticmethod
    @Logger.log_call
    def load_from_database(database) -> dict:
        with UserManager._mutex:
            UserManager.update_fields()
            raise NotImplementedError("Загрузка из базы данных не реализована")

    @staticmethod
    @Logger.log_call
    def save_to_database(database, dictionary: dict) -> bool:
        UserManager.update_fields()
        raise NotImplementedError("Сохранение в базу данных не реализовано")

    @staticmethod
    @Logger.log_call
    def find_user(user_id: int = None, user_login: str = None) -> User | None:
        UserManager.update_fields()
        if user_id is not None:
            if isinstance(user_id, str):
                user_id = int(user_id)
            if not isinstance(user_id, int):
                raise ValueError("user_id должен быть целым числом или строкой, представляющей число")
            return UserManager._users.get(user_id)
        if user_login:
            user_login = user_login.lower()
            if not isinstance(user_login, str):
                raise ValueError("user_login должен быть строкой")
            for user in UserManager._users.values():
                if user.authorization_data["login"] == user_login:
                    return user
        return None

    @staticmethod
    @Logger.log_call
    def new_user(user_login: str, user_group: User.Group = User.Group.COMMON):
        user_login = user_login.lower()
        with UserManager._mutex:
            if not isinstance(user_group, User.Group):
                raise ValueError("user_group должен быть экземпляром User.Group")
            if user_login in UserManager._busy_logins:
                raise ValueError(f"Логин {user_login} уже занят")
            new_id = UserManager._user_count + 1
            if new_id in UserManager._busy_id:
                raise ValueError(f"Ошибка генерации нового id: {new_id}")
            new_user = User(user_id=new_id, user_login=user_login, user_group=user_group)
            UserManager._users[new_id] = new_user
            UserManager._busy_logins.add(user_login)
            UserManager._busy_id.add(new_id)
            UserManager.update_fields()
            return new_user

    @staticmethod
    @Logger.log_call
    def delete_user(user_id: int = None, user_login: str = None) -> bool:
        if user_login is not None:
            user_login = user_login.lower()
        with UserManager._mutex:
            if user_id is not None:
                if user_id not in UserManager._users:
                    raise ValueError(f"Удаление пользователя {user_id} невозможно: Пользователь не существует")
                del UserManager._users[user_id]
                UserManager._busy_id.discard(user_id)
                print(f"Пользователь с id: {user_id} удален")
                UserManager.update_fields()
                return True

            if user_login is not None:
                user = UserManager.find_user(user_login=user_login)
                if user is None:
                    raise ValueError(f"Удаление пользователя {user_login} невозможно: Пользователь не существует")
                del UserManager._users[user.user_id]
                UserManager._busy_logins.discard(user_login)
                UserManager._busy_id.discard(user.user_id)
                print(f"Пользователь с id: {user.user_id} удален")
                UserManager.update_fields()
                return True
            raise ValueError("Необходимо передать user_id или user_login для удаления пользователя")


class Permission:

    @staticmethod
    @Logger.log_call
    def check(user: User, group: User.Group) -> bool:
        if user.user_group == group:
            return True
        else:
            return False

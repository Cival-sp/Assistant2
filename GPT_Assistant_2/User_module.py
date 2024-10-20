from enum import Enum
from Assistant_core import AssistantLogicCore
from GPT_Assistant_2.GPT_module import OpenAiGPT


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
    system_prompt = str or None

    def __init__(self):
        self.person = Person()
        self.user_prompt = None
        self.model=OpenAiGPT()


class User:
    class Group(Enum):
        OWNER = "Владелец"
        ADMIN = "Администратор"
        VIP = "Привилегированный пользователь"
        COMMON = "Пользователь"
        GUEST = "Гость"
        BANNED = "Заблокирован"

    def __init__(self, user_id, user_name=None):
        self.user_id = user_id
        self.user_avatar = None
        self.user_group = User.Group.GUEST
        self.human_person = Person(user_name)
        self.person_assistant = Assistant()
        self.user_contacts = {
            "mobile_phone": None,
            "email": None
        }
        self.settings = {}
        self.additional_info = {
            "token_used": 0,
            "last_seen":None
        }
        self.authorization_data = {}

    def export_to_dict(self):
        return {
            "user_id": self.user_id,
            "user_avatar": self.user_avatar,
            "human_person": self.human_person,
            "person_assistant": self.person_assistant,
            "user_contacts": self.user_contacts,
            "settings": self.settings,
            "additional_info": self.additional_info
        }
    @staticmethod
    def init_default_user(user_id):
        user=User(user_id,"Гость")
        user.user_avatar=None
        return user

class UserDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.description = None


class DeviceManager:
    def __init__(self):
        self.ownership = {  # user_id: [device_id]
            # 1:[1,2,3]
        }

    def assign_device_for_user(self, user_id, device_id):
        self.ownership[user_id].append(device_id)

    def delete_device_for_user(self, user_id, device_id):
        self.ownership[user_id].remove(device_id)

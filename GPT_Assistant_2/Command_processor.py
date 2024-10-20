from Utility import validate_json
from Assistant_core import AssistantAnswer


class Command:
    def __init__(self, name=None, parameters=None, description=None):
        """
        Конструктор класса Command.
        :param name: Название команды (строка).
        :param parameters: Словарь с параметрами команды.
        """
        self.name = name
        self.parameters = parameters if parameters is not None else {}
        self.command_description = description

    @staticmethod
    def from_json(json_dict):
        """
        Создает объект Command из словаря JSON.
        :param json_dict: Словарь JSON, содержащий данные для инициализации объекта.
        :return: Экземпляр Command.
        """
        json_dict = validate_json(json_dict)
        return Command(
            name=json_dict.get("name"),
            parameters=json_dict.get("parameters", {})
        )

    def to_json(self):
        """
        Преобразует объект Command в словарь JSON.
        :return: Словарь JSON, представляющий объект Command.
        """
        return {
            "name": self.name,
            "parameters": self.parameters
        }


class CommandList:
    def __init__(self, commands=None):
        self.commands = commands or []

    def append(self, command):
        self.commands.append(command)

    def format_description_string(self):
        result_str = "Доступные команды. Формат команды - имя(параметры)|Описание команды"
        for command in self.commands:
            result_str += f"{command.name}({command.parameters})|{command.command_description},)"
            return result_str

    def __str__(self):
        result_str = ""
        for command in self.commands:
            result_str += f"{command.name}({command.parameters}),)"
        return result_str


class CommandProcessor:
    def __init__(self, command_object_list=None):
        self.command_object_list = command_object_list or []  # Список объектов, содержащих методы для выполнения

    def parse_command(self, assistant_answer):
        try:
            if isinstance(assistant_answer, AssistantAnswer):
                if assistant_answer.command is not None:
                    return assistant_answer.command
            if isinstance(assistant_answer, Command):
                return assistant_answer
            if isinstance(assistant_answer, (dict, str)):
                cmd = Command.from_json(assistant_answer)
                return cmd if cmd.name in self.command_object_list else None
        except Exception as e:
            print(f"Ошибка при поиске команды: {e}")
            return None

    def find_command(self, command):
        """Ищет метод на основе объекта Command и возвращает ссылку на метод, если он найден."""
        for command_object in self.command_object_list:  # Итерируемся по всем объектам в списке
            method = getattr(command_object, command.name, None)  # Получаем метод по имени
            if callable(method):
                return method
        raise AttributeError(f"Команда {command.name} не найдена")

    def execute_command(self, command):
        """Выполняет команду на основе объекта Command."""
        try:
            method = self.find_command(command)
            return method(**command.parameters)
        except Exception as e:
            error_str = f"Ошибка при вызове команды: {e}"
            print(error_str)
            return error_str

    def is_command_exist(self, command):  # Не проходит тест
        if self.find_command(command) is not None:
            return True
        else:
            return False


if __name__ == '__main__':
    class test:
        def __init__(self):
            self.what = None

        def woof(self):
            return "hello"

        def meow(self, text):
            return text


    obj1 = test()
    obj2 = test()
    objlist = [obj1, obj2]

    CmdProcessor = CommandProcessor(command_object_list=objlist)
    com1 = Command("woof", None)
    com2 = Command("woof")
    com3 = Command("meow", {"text": "this is param"})
    CmdProcessor.execute_command(com3)

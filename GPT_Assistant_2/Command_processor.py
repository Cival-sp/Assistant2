from Utility import validate_json

class Command:
    def __init__(self, name=None, parameters=None, description=None):
        """
        Конструктор класса Command. Представляет команду, которую можно выполнить,
        с именем, параметрами и описанием.

        :param name: Название команды (строка).
        :param parameters: Словарь с параметрами команды (dict, по умолчанию None).
        :param description: Описание команды (строка, по умолчанию None).
        """
        self.name = name
        self.parameters = parameters if parameters is not None else {}
        self.command_description = description

    @staticmethod
    def from_json(json_dict):
        """
        Создает объект Command из JSON-словаря. Валидация JSON осуществляется
        с помощью метода validate_json из модуля Utility.

        :param json_dict: Словарь JSON, содержащий данные для инициализации объекта.
                          Ожидается, что словарь содержит ключи "name" (строка) и
                          "parameters" (словарь параметров команды).
        :return: Экземпляр Command, инициализированный данными из JSON.
        """
        json_dict = validate_json(json_dict)
        return Command(
            name=json_dict.get("name"),
            parameters=json_dict.get("parameters", {})
        )

    def to_json(self):
        """
        Преобразует объект Command в словарь JSON, чтобы его можно было сериализовать.

        :return: Словарь JSON, представляющий объект Command, с ключами "name" и "parameters".
        """
        return {
            "name": self.name,
            "parameters": self.parameters
        }


class CommandList:
    def __init__(self, commands=None):
        """
        Конструктор класса CommandList. Хранит список команд.

        :param commands: Список объектов Command (по умолчанию None).
                         Если None, инициализирует пустой список команд.
        """
        self.commands = commands or []

    def append(self, command):
        """
        Добавляет команду в список команд.

        :param command: Объект Command, который нужно добавить в список.
        """
        self.commands.append(command)

    def format_description_string(self):
        """
        Форматирует описание доступных команд для отображения.
        Формат: "имя команды(параметры)|Описание команды".

        :return: Строка, представляющая описание всех команд.
        """
        result_str = "Доступные команды. Формат команды - имя(параметры)|Описание команды"
        for command in self.commands:
            result_str += f"{command.name}({command.parameters})|{command.command_description},"
        return result_str

    def __str__(self):
        """
        Возвращает строковое представление списка команд для удобства отображения.

        :return: Строка, представляющая все команды в формате "имя(параметры)".
        """
        result_str = ""
        for command in self.commands:
            result_str += f"{command.name}({command.parameters}),"
        return result_str


class CommandProcessor:
    def __init__(self, command_object_list=None):
        """
        Конструктор класса CommandProcessor. Отвечает за выполнение команд, используя
        объекты с методами, которые можно вызвать по имени команды.

        :param command_object_list: Список объектов, содержащих методы, доступные для выполнения
                                    по командам (по умолчанию None). Если None, инициализирует
                                    пустой список объектов.
        """
        self.command_object_list = command_object_list or []

    def find_command(self, command):
        """
        Ищет метод в списке объектов command_object_list на основе имени команды и возвращает
        ссылку на метод, если он найден.

        :param command: Объект Command, содержащий имя команды для поиска.
        :return: Ссылка на метод, если найден; иначе, вызывает AttributeError.
        :raises AttributeError: Если метод с указанным именем не найден ни в одном объекте.
        """
        for command_object in self.command_object_list:
            method = getattr(command_object, command.name, None)
            if callable(method):
                return method
        raise AttributeError(f"Команда {command.name} не найдена")

    def execute_command(self, command):
        """
        Выполняет команду, вызывая соответствующий метод с переданными параметрами.

        :param command: Объект Command, содержащий имя и параметры для выполнения.
        :return: Результат выполнения команды (любой тип данных, возвращаемый методом).
        :raises Exception: Возникает при ошибке вызова метода, возвращает строку с описанием ошибки.
        """
        try:
            method = self.find_command(command)
            return method(**command.parameters)
        except Exception as e:
            error_str = f"Ошибка при вызове команды: {e}"
            print(error_str)
            return error_str

    def is_command_exist(self, command):
        """
        Проверяет, существует ли метод, соответствующий имени команды.

        :param command: Объект Command, содержащий имя команды для проверки.
        :return: True, если метод найден и доступен для вызова, иначе False.
        """
        try:
            self.find_command(command)
            return True
        except AttributeError:
            return False


if __name__ == '__main__':
    class Test:
        def __init__(self):
            self.what = None

        def woof(self):
            return "Woof, motherfucker"

        def meow(self, text):
            return text

    obj1 = Test()
    obj2 = Test()
    objlist = [obj1, obj2]

    CmdProcessor = CommandProcessor(command_object_list=objlist)
    com1 = Command("woof", None,"Простая команда")
    com2 = Command("woof")
    com3 = Command("meow", {"text": "this is param"},"бесполезное описание")
    print(CmdProcessor.execute_command(com1))
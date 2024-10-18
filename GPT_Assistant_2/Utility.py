import os
import json


def validate_json(json_data):
    """
    Проверяет и валидирует входные данные JSON.
    :param json_data: Входные данные, которые могут быть строкой JSON или словарем.
    :return: Словарь, если входные данные валидны, или None в противном случае.
    """
    if isinstance(json_data, str):
        try:
            result = json.loads(json_data)
            return result
        except json.JSONDecodeError:
            return None
    elif isinstance(json_data, dict):
        return json_data
    else:
        return None

def is_allowed(value, valid_value_list):
    if value in valid_value_list:
        return True
    else:
        return False


class AudioFile:
    def __init__(self, FileName=None, FileExtension=None, Body=None):
        self.name = FileName
        self.extension = FileExtension
        self.body = Body

    @classmethod
    def from_path(cls, file_path):
        """
        Конструктор обьекта из строки пути к файлу
        :param file_path: Любой корректный путь к файлу формата Путь/путь/имя.расширение или имя.расширение
        :return:
        """
        base_name = os.path.basename(file_path)
        try:
            name, extension = base_name.rsplit('.', 1)
            return cls(FileName=name, FileExtension=extension)
        except ValueError:
            raise ValueError("Строка должна содержать имя файла с расширением в формате 'имя.расширение'")
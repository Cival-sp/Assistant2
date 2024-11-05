import os
import json


def validate_data(DATA, CLASS):
    if not isinstance(DATA, CLASS):
        raise AttributeError(
            f"В метод передан объект {type(DATA)} вместо {type(CLASS)}")
    return True


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


class File:
    def __init__(self, name, extension, body=None):
        """
        Базовый класс для представления файла.

        :param name: Имя файла без расширения.
        :param extension: Расширение файла.
        :param body: Содержимое файла, если доступно (по умолчанию None).
        """
        self.name = name
        self.extension = extension
        self.body = body

    @classmethod
    def from_path(cls, file_path):
        """
        Создает экземпляр File из строки пути к файлу.

        :param file_path: Корректный путь к файлу в формате 'путь/имя.расширение' или просто 'имя.расширение'.
        :return: Экземпляр класса File.
        """
        base_name = os.path.basename(file_path)  # Извлекает только имя файла с расширением
        try:
            # Разделяет имя и расширение файла
            name, extension = base_name.rsplit('.', 1)

            # Открывает и считывает содержимое файла
            with open(file_path, 'rb') as file:
                body = file.read()

            return cls(name=name, extension=extension, body=body)

        except ValueError:
            raise ValueError("Строка должна содержать имя файла с расширением в формате 'имя.расширение'")
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл по пути {file_path} не найден")


class AudioFile(File):
    def __init__(self, name, extension, body=None):
        """
        Класс для представления аудиофайла. Наследует класс File.

        :param name: Имя файла без расширения.
        :param extension: Расширение файла.
        :param body: Содержимое файла (по умолчанию None).
        """
        super().__init__(name, extension, body)

    @classmethod
    def from_file(cls, file: File):
        """
        Создает объект AudioFile из существующего объекта File, если его расширение соответствует аудиофайлу.

        :param file: Экземпляр File.
        :return: Экземпляр AudioFile.
        """
        valid_audio_extensions = ['mp3', 'wav', 'flac', 'ogg', 'webm']
        if file.extension.lower() not in valid_audio_extensions:
            raise ValueError(
                f"Файл {file.name} не является аудиофайлом. Допустимые расширения: {', '.join(valid_audio_extensions)}")

        return cls(name=file.name, extension=file.extension, body=file.body)

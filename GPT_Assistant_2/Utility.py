import os

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
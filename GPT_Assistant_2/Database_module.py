from Assistant_core import Session
from abc import ABC, abstractmethod
import os
import pickle


class Database:

    @abstractmethod
    def save_user_sessions(self, session_array):
        pass

    @abstractmethod
    def load_user_sessions(self, user_id):
        pass


class FileDatabase:
    def __init__(self, base_dir="../Database"):
        self.session_base_dir = base_dir
        if not os.path.exists(self.session_base_dir):
            os.makedirs(self.session_base_dir)

    def save_user_sessions(self, session_array):
        """
        Сохраняет массив сессий в файлы. Каждая сессия сохраняется в файл с именем user_id.
        Если файл уже существует, данные дозаписываются.

        Аргументы:
            session_array: список объектов сессий
        """
        count = 0
        for session in session_array:
            output_filepath = os.path.join(self.session_base_dir, f"{session.user_id}.pkl")
            with open(output_filepath, "ab") as file:
                pickle.dump(session, file)
                count += 1
        print(f"{count} сессий успешно сохранено.")

    def load_user_sessions(self, user_id):
        """
        Читает и возвращает все сессии пользователя из файла.

        Аргументы:
            user_id: идентификатор пользователя, для которого нужно загрузить сессии

        Возвращает:
            список объектов сессий, либо пустой список, если файл не существует
        """
        input_filepath = os.path.join(self.session_base_dir, f"{user_id}.pkl")
        sessions = []
        count=0
        if os.path.exists(input_filepath):
            with open(input_filepath, "rb") as file:
                try:
                    while True:
                        session = pickle.load(file)
                        sessions.append(session)
                        count += 1
                except EOFError:
                    pass
        print(f"Загружено {count} сессий")
        return sessions

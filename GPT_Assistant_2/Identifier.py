

class IDPool:
    def __init__(self, max_id=0xFFFFFFFE):
        """
        Инициализация пула ID с максимальным числом ID.
        :param max_id: Максимальное количество доступных ID.
        """
        self.free_ids = set(range(1, max_id + 1))  # Свободные ID
        self.issued_ids = {}  # Словарь для хранения выданных ID {ID: уникальная строка}

    def get_id(self, unique_string):
        """
        Выдача ID для заданной уникальной строки.
        :param unique_string: Уникальная строка, идентифицирующая пользователя.
        :return: ID в виде строки.
        """
        # Проверяем, не выдан ли уже ID для этой уникальной строки
        for id_, stored_string in self.issued_ids.items():
            if stored_string == unique_string:
                return str(id_)

        # Если свободные ID доступны, выдаем новый
        if self.free_ids:
            new_id = self.free_ids.pop()
            self.issued_ids[new_id] = unique_string
            return str(new_id)
        else:
            raise Exception("Нет доступных свободных ID")

    def release_id(self, id_):
        """
        Освобождает ID, возвращая его в пул.
        :param id_: ID для освобождения.
        """
        id_ = int(id_)
        if id_ in self.issued_ids:
            del self.issued_ids[id_]
            self.free_ids.add(id_)

    def get_info(self, id_):
        """
        Получение информации об уникальной строке для заданного ID.
        :param id_: ID для поиска.
        :return: Уникальная строка, если ID существует, иначе None.
        """
        return self.issued_ids.get(id_)

    def take_id(self, id_, unique_string):
        """
        Запрашивает конкретный ID, если он свободен, и выдает его для заданной уникальной строки.
        :param id_: Запрашиваемый ID.
        :param unique_string: Уникальная строка, идентифицирующая пользователя.
        :return: Запрашиваемый ID в виде строки, если он свободен, иначе исключение.
        """
        id_ = int(id_)
        if id_ in self.free_ids:
            self.free_ids.remove(id_)
            self.issued_ids[id_] = unique_string
            return str(id_)
        elif id_ in self.issued_ids:
            raise Exception(f"ID {id_} уже выдан")
        else:
            raise Exception(f"ID {id_} вне допустимого диапазона")
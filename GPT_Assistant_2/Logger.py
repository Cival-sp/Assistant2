import os
import datetime

class Logger:
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }
    name = "DefaultLogger"
    level = LEVELS["INFO"]
    log_file = None

    @staticmethod
    def configure(name="DefaultLogger", level="INFO", log_file=None):
        """
        Настройка логгера.
        :param name: Имя логгера.
        :param level: Уровень логирования (например, "DEBUG").
        :param log_file: Путь к файлу для сохранения логов (если указан).
        """
        Logger.name = name
        Logger.level = Logger.LEVELS.get(level.upper(), 20)
        Logger.log_file = log_file
        if Logger.log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(Logger.log_file, 'a') as f:
                f.write(f"Logger {Logger.name} started.\n")

    @staticmethod
    def _log(level_name, message):
        if Logger.LEVELS[level_name] >= Logger.level:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"{timestamp} - {Logger.name} - {level_name} - {message}"
            print(log_message)
            if Logger.log_file:
                with open(Logger.log_file, 'a') as f:
                    f.write(log_message + "\n")

    @staticmethod
    def debug(message): Logger._log("DEBUG", message)
    @staticmethod
    def info(message): Logger._log("INFO", message)
    @staticmethod
    def warning(message): Logger._log("WARNING", message)
    @staticmethod
    def error(message): Logger._log("ERROR", message)
    @staticmethod
    def critical(message): Logger._log("CRITICAL", message)

    @staticmethod
    def log_call(func):
        def wrapper(*args, **kwargs):
            Logger.info(f"Вызов функции {func.__name__} с аргументами {args} и {kwargs}")
            result = func(*args, **kwargs)
            Logger.info(f"Функция {func.__name__} вернула {result}")
            return result
        return wrapper

Logger.configure(name="AppLogger", level="DEBUG")


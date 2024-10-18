from abc import ABC
import pickle


class ApiInterface(ABC):
    contain_folder = "Api"

    def __init__(self, url=None, token=None):
        self.url = url
        self.token = token
        self.api_name = ""
        self.description = ""

    def save_to_file(self, filepath):
        with open(ApiInterface.contain_folder + '/' + self.api_name, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load_from_file(filename):
        with open(ApiInterface.contain_folder + '/' + filename, 'rb') as file:
            api_object = pickle.load(file)
            return api_object


class MusicApi(ApiInterface):
    def play_track(self, author, track):
        pass

    def find_track(self, track):
        pass

    def search_track(self, author, track_name):
        pass


class NewsApi(ApiInterface):
    pass


class WeatherApi(ApiInterface):
    def current_weather(self, city):
        pass


class CalendarApi(ApiInterface):
    pass


class EmailApi(ApiInterface):
    def send_email(self, to, subject, body):
        pass

    def check_mail(self):
        pass


class SmartHomeApi(ApiInterface):
    pass


class MessengerApi(ApiInterface):
    def send_message(self, to, message):
        pass

    def check_messages(self):
        pass

    def get_message(self, message_id):
        pass

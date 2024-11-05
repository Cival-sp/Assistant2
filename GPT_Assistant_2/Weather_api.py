from GPT_Assistant_2.Extern_api_declaration import WeatherApi
from GPT_Assistant_2.Command_processor import Command
import requests


class OpenWeather(WeatherApi):
    def __init__(self, api_key=None):
        WeatherApi.__init__(self, api_key)
        self.api_name = 'OpenWeather'
        self.description = """OpenWeather API предоставляет доступ к различным метеорологическим данным, включая текущую погоду, прогнозы и исторические данные о погоде."""
        self.current_weather_url = "http://api.openweathermap.org/data/2.5/weather"
        self.week_forcast_url = "http://api.openweathermap.org/data/2.5/forecast"
        self.api_key = api_key
        self.available_commands = [Command(
            "current_weather",
            "city",
            "Запрашивает погоду и температуру на текущий день в заданном городе. Принимает один параметр")
        ]

    def current_weather_in_city(self, city=None):
        result = requests.get(self.current_weather_url, params={'q': city, 'appid': self.api_key, 'units': 'metric'})
        if result.status_code != 200:
            raise RuntimeError(f"Ошибка запроса к OpenWeather api. code={result.status_code}")
        temp = result.json()['main']['temp']
        weather_description = result.json()['weather'][0]['description']
        result_str = f"Температура в {city}: {temp}°C, {weather_description}."
        return result_str


class OpenMeteo(WeatherApi):
    def __init__(self, api_key=None):
        WeatherApi.__init__(self, api_key)
        self.api_name = 'Openmeteo'
        self.available_commands = None
        self.token = api_key
        self.url = "https://api.open-meteo.com/v1/forecast"
        self.available_commands = [Command(
            "current_weather_by_coords",
            ["latitude", "longitude"],
            "Запрос погоды по координатам"
        )]

    def current_weather_by_coords(self, lat, lon):
        params = {'latitude': lat, 'longitude': lon, "current": ["temperature", "relative_humidity_2m"]}
        result = requests.get(self.url, params=params)
        if result.status_code != 200:
            raise RuntimeError(f"Ошибка запроса к Open-meteo api. Код ошибки={result.status_code}")
        return result.json()

if __name__ == "__main__":
    try:
        weather_api = OpenMeteo()
        cmd=weather_api.available_commands[0]
        print(weather_api.current_weather_by_coords(56.111679, 37.424689))
    except Exception as e:
        print(e)

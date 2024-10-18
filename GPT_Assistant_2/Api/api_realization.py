from ..Extern_api_declaration import WeatherApi
import requests
import json


class OpenWeather(WeatherApi):
    def __init__(self, api_key=None):
        WeatherApi.__init__(self)
        self.api_name = 'OpenWeather'
        self.description = """OpenWeather API предоставляет доступ к различным метеорологическим данным, включая текущую погоду, прогнозы и исторические данные о погоде."""
        self.current_weather_url = "http://api.openweathermap.org/data/2.5/weather"
        self.week_forcast_url = "http://api.openweathermap.org/data/2.5/forecast"
        self.api_key = api_key

    def current_weather(self, city):
        result = requests.get(self.current_weather_url, params={'q': city, 'appid': self.api_key, 'units': 'metric'})
        if result.status_code != 200:
            raise RuntimeError(f"Ошибка запроса к OpenWeather api. code={result.status_code}")
        temp = result.json()['main']['temp']
        weather_description = result.json()['weather'][0]['description']
        result_str = f"Температура в {city}: {temp}°C, {weather_description}."
        return result_str

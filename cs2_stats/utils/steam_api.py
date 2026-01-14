import os
import requests
from django.conf import settings


class SteamAPI:
    """
    Класс для взаимодействия с Steam Web API.
    Предоставляет методы для получения данных игроков и времени игры.
    Требуется Steam API ключ в настройках Django.
    """

    def __init__(self):
        """Инициализация с ключом API из настроек Django."""
        self.api_key = settings.STEAM_API_KEY  # Ключ из .env файла
        self.base_url = "https://api.steampowered.com"  # Базовый URL Steam API

    def get_player_summary(self, steam_id):
        """
        Получает основную информацию об игроке из Steam.

        Args:
            steam_id (str): Уникальный Steam ID игрока

        Returns:
            dict: Данные игрока или None при ошибке
            Содержит: nickname, avatar, country, profileurl и др.
        """
        url = f"{self.base_url}/ISteamUser/GetPlayerSummaries/v2/"
        params = {
            'key': self.api_key,  # API ключ для аутентификации
            'steamids': steam_id  # Steam ID для поиска
        }

        try:
            # Отправляем GET запрос к Steam API
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Проверяем статус ответа
            data = response.json()  # Парсим JSON ответ

            # Извлекаем данные первого игрока из массива players
            if data.get('response', {}).get('players'):
                player_data = data['response']['players'][0]
                return player_data
        except Exception as e:
            # Логируем ошибку, но не прерываем выполнение
            print(f"Steam API error: {e}")

        return None  # Возвращаем None при ошибке или отсутствии данных

    def get_cs2_playtime(self, steam_id):
        """
        Получает время игры в Counter-Strike 2 для указанного игрока.

        Args:
            steam_id (str): Steam ID игрока

        Returns:
            float: Количество часов в CS2, округленное до 1 десятичного знака
                   Возвращает 0 если игра не найдена или при ошибке
        """
        url = f"{self.base_url}/IPlayerService/GetOwnedGames/v1/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'include_appinfo': 0,  # Не включать информацию об играх
            'include_played_free_games': 1,  # Включать бесплатные игры
            'appids_filter[0]': 730  # App ID CS2 (730)
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Ищем CS2 в списке игр игрока
            games = data.get('response', {}).get('games', [])
            for game in games:
                if game.get('appid') == 730:  # CS2 App ID
                    # playtime_forever в минутах, конвертируем в часы
                    return round(game.get('playtime_forever', 0) / 60, 1)
        except Exception as e:
            print(f"Steam API playtime error: {e}")

        return 0  # Возвращаем 0 часов при ошибке или отсутствии игры
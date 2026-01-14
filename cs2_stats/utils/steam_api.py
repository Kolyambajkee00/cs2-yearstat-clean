import os
import requests
from django.conf import settings


class SteamAPI:
    """Класс для работы с Steam Web API"""

    def __init__(self):
        self.api_key = settings.STEAM_API_KEY
        self.base_url = "https://api.steampowered.com"

    def get_player_summary(self, steam_id):
        """Получить информацию об игроке"""
        url = f"{self.base_url}/ISteamUser/GetPlayerSummaries/v2/"
        params = {
            'key': self.api_key,
            'steamids': steam_id
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('response', {}).get('players'):
                player_data = data['response']['players'][0]
                return player_data
        except Exception as e:
            print(f"Steam API error: {e}")

        return None

    def get_cs2_playtime(self, steam_id):
        """Получить время игры в CS2 (в часах)"""
        url = f"{self.base_url}/IPlayerService/GetOwnedGames/v1/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'include_appinfo': 0,
            'include_played_free_games': 1,
            'appids_filter[0]': 730  # CS2 App ID
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            games = data.get('response', {}).get('games', [])
            for game in games:
                if game.get('appid') == 730:  # CS2
                    return round(game.get('playtime_forever', 0) / 60, 1)  # Минуты в часы
        except Exception as e:
            print(f"Steam API playtime error: {e}")

        return 0

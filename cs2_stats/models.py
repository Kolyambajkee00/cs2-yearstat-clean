# cs2_stats/models.py
from django.db import models
from django.utils import timezone


class Player(models.Model):
    """
    Модель игрока CS2. Хранит данные из Steam API.
    Связана с MonthlyStat через ForeignKey.
    """
    steam_id = models.CharField(max_length=20, unique=True)  # Уникальный Steam ID
    nickname = models.CharField(max_length=100, blank=True)  # Ник из Steam
    avatar = models.URLField(max_length=500, blank=True)     # URL аватара
    country = models.CharField(max_length=10, blank=True)    # Код страны (RU, US, etc.)
    cs2_hours = models.FloatField(default=0)                 # Часы в CS2
    last_updated = models.DateTimeField(auto_now=True)       # Время последнего обновления

    def __str__(self):
        return f"{self.nickname} ({self.steam_id})"

    def update_from_steam(self):
        """
        Обновляет данные игрока из Steam API.
        Возвращает True при успехе, False при ошибке.
        """
        try:
            from .utils.steam_api import SteamAPI
            steam_api = SteamAPI()

            # Получаем базовую информацию об игроке
            player_data = steam_api.get_player_summary(self.steam_id)

            if player_data:
                self.nickname = player_data.get('personaname', self.nickname)
                self.avatar = player_data.get('avatarfull', self.avatar)

                # Страна может быть не указана в Steam профиле
                country_code = player_data.get('loccountrycode')
                if country_code:
                    self.country = country_code
                else:
                    self.country = ''  # Пустая строка если нет страны

            # Получаем время игры в CS2
            playtime = steam_api.get_cs2_playtime(self.steam_id)
            if playtime > 0:
                self.cs2_hours = playtime

            self.last_updated = timezone.now()
            self.save()
            return True

        except Exception as e:
            print(f"Error updating from Steam: {e}")
            return False


class MonthlyStat(models.Model):
    """
    Модель месячной статистики игрока.
    Один игрок (Player) может иметь много записей MonthlyStat.
    """
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'),
        (4, 'April'), (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'), (9, 'September'),
        (10, 'October'), (11, 'November'), (12, 'December')
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='monthly_stats')
    year = models.IntegerField(default=2025)
    month = models.IntegerField(choices=MONTH_CHOICES)

    # Данные, вводимые пользователем
    matches_played = models.IntegerField(default=0)  # Сыгранные матчи
    kills = models.IntegerField(default=0)          # Убийства
    deaths = models.IntegerField(default=0)         # Смерти
    wins = models.IntegerField(default=0)           # Победы

    class Meta:
        unique_together = ['player', 'year', 'month']  # Одна запись на месяц для игрока
        ordering = ['-year', '-month']  # Сортировка от новых к старым

    def __str__(self):
        return f"{self.player.nickname} - {self.year}/{self.month}"

    @property
    def kd_ratio(self):
        """Расчет K/D ratio (убийства/смерти)."""
        if self.deaths > 0:
            return round(self.kills / self.deaths, 2)
        return 0.0

    @property
    def win_rate(self):
        """Расчет процента побед (победы/матчи * 100%)."""
        if self.matches_played > 0:
            return round((self.wins / self.matches_played) * 100, 1)
        return 0.0
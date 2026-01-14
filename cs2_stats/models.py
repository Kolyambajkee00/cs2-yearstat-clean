# cs2_stats/models.py
from django.db import models
from django.utils import timezone


class Player(models.Model):
    """CS2 Player"""
    steam_id = models.CharField(max_length=20, unique=True)
    nickname = models.CharField(max_length=100, blank=True)
    avatar = models.URLField(max_length=500, blank=True)
    country = models.CharField(max_length=10, blank=True)
    cs2_hours = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nickname} ({self.steam_id})"

    def update_from_steam(self):
        """Update player data from Steam API"""
        try:
            from .utils.steam_api import SteamAPI
            steam_api = SteamAPI()

            # Get data from Steam
            player_data = steam_api.get_player_summary(self.steam_id)

            if player_data:
                self.nickname = player_data.get('personaname', self.nickname)
                self.avatar = player_data.get('avatarfull', self.avatar)

                # Получаем страну - может быть None если не указана в Steam
                country_code = player_data.get('loccountrycode')
                if country_code:
                    self.country = country_code
                else:
                    self.country = ''  # Пустая строка если нет страны

            # Get playtime
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
    """Monthly statistics"""
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'),
        (4, 'April'), (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'), (9, 'September'),
        (10, 'October'), (11, 'November'), (12, 'December')
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='monthly_stats')
    year = models.IntegerField(default=2025)
    month = models.IntegerField(choices=MONTH_CHOICES)

    # User input
    matches_played = models.IntegerField(default=0)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)

    class Meta:
        unique_together = ['player', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.player.nickname} - {self.year}/{self.month}"

    @property
    def kd_ratio(self):
        """Calculate K/D ratio"""
        if self.deaths > 0:
            return round(self.kills / self.deaths, 2)
        return 0.0

    @property
    def win_rate(self):
        """Calculate win rate"""
        if self.matches_played > 0:
            return round((self.wins / self.matches_played) * 100, 1)
        return 0.0

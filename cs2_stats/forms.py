from django import forms
from .models import MonthlyStat


class MonthlyStatForm(forms.ModelForm):
    """
    Форма для добавления и редактирования месячной статистики.
    Включает валидацию данных и проверку уникальности.
    """

    class Meta:
        model = MonthlyStat
        fields = ['year', 'month', 'matches_played', 'kills', 'deaths', 'wins']

        # Кастомизация виджетов для Bootstrap стилей
        widgets = {
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2024,  # Минимальный год
                'max': 2026,  # Максимальный год
                'value': 2025  # Значение по умолчанию
            }),
            'month': forms.Select(attrs={'class': 'form-control'}),  # Выпадающий список месяцев
            'matches_played': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,  # Не может быть отрицательным
                'placeholder': 'e.g., 50'  # Пример для пользователя
            }),
            'kills': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'e.g., 500'
            }),
            'deaths': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'e.g., 400'
            }),
            'wins': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'e.g., 30'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы с игроком.
        player передается из views для проверки уникальности.
        """
        self.player = kwargs.pop('player', None)  # Игрок для валидации
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Валидация данных формы.
        Проверяет:
        1. Победы не больше матчей
        2. Уникальность месяца для игрока
        """
        cleaned_data = super().clean()
        matches = cleaned_data.get('matches_played')
        wins = cleaned_data.get('wins')
        year = cleaned_data.get('year')
        month = cleaned_data.get('month')

        # Проверка 1: Победы не могут превышать количество матчей
        if matches is not None and wins is not None:
            if wins > matches:
                # Привязываем ошибку к полю 'wins' для отображения рядом с ним
                self.add_error('wins', "Wins cannot be greater than matches played!")

        # Проверка 2: Уникальность комбинации игрок-год-месяц
        if self.player and year and month:
            # Проверяем существует ли уже статистика за этот месяц
            existing = MonthlyStat.objects.filter(
                player=self.player,
                year=year,
                month=month
            ).exists()

            # Если редактируем существующую запись
            if self.instance and self.instance.pk:
                # Это редактирование, проверяем только если месяц изменился
                if not (self.instance.year == year and self.instance.month == month):
                    if existing:
                        self.add_error('month',
                                       f"Statistics for {year}/{month} already exist! "
                                       "Please edit the existing entry instead."
                                       )
            else:
                # Это создание новой записи
                if existing:
                    self.add_error('month',
                                   f"Statistics for {year}/{month} already exist! "
                                   "Please edit the existing entry instead."
                                   )

        return cleaned_data
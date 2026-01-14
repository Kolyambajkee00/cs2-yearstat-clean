from django import forms
from .models import MonthlyStat


class MonthlyStatForm(forms.ModelForm):
    """Форма для ввода статистики за месяц"""

    class Meta:
        model = MonthlyStat
        fields = ['year', 'month', 'matches_played', 'kills', 'deaths', 'wins']
        widgets = {
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2024,
                'max': 2026,
                'value': 2025
            }),
            'month': forms.Select(attrs={'class': 'form-control'}),
            'matches_played': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'e.g., 50'
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
        self.player = kwargs.pop('player', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """Валидация данных"""
        cleaned_data = super().clean()
        matches = cleaned_data.get('matches_played')
        wins = cleaned_data.get('wins')
        year = cleaned_data.get('year')
        month = cleaned_data.get('month')

        # Проверка: победы не больше матчей
        if matches is not None and wins is not None:
            if wins > matches:
                # Привязываем ошибку к полю 'wins'
                self.add_error('wins', "Wins cannot be greater than matches played!")

        # Проверка: уникальность месяца для игрока
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
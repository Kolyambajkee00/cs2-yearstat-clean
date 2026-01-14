from django.contrib import messages
from django.contrib import admin
from .models import Player, MonthlyStat


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели Player.
    Добавляет кнопку обновления данных из Steam API.
    """
    # Поля, отображаемые в списке игроков
    list_display = ('nickname', 'steam_id', 'country', 'cs2_hours', 'last_updated', 'update_button')
    search_fields = ('nickname', 'steam_id')  # Поиск по нику и Steam ID
    list_filter = ('country', 'last_updated')  # Фильтры по стране и дате обновления

    # Поля в форме редактирования
    fields = ('steam_id', 'nickname', 'avatar', 'country', 'cs2_hours', 'last_updated')
    readonly_fields = ('last_updated',)  # Поле только для чтения

    # Кнопка обновления из Steam API
    def update_button(self, obj):
        """
        Создает HTML кнопку для обновления данных игрока из Steam.
        Отображается в списке игроков.
        """
        from django.utils.html import format_html
        return format_html(
            '<a href="update-steam/{}/" style="background: #28a745; color: white; '
            'padding: 5px 10px; border-radius: 3px; text-decoration: none; '
            'display: inline-block;">🔄 Update from Steam</a>',
            obj.id
        )

    update_button.short_description = 'Actions'  # Заголовок колонки

    # Добавляем кастомный URL для обновления через админку
    def get_urls(self):
        """
        Добавляет кастомный URL endpoint для обновления данных из Steam.
        """
        from django.urls import path
        from django.shortcuts import redirect

        urls = super().get_urls()

        def update_view(request, player_id):
            """
            Обработчик для обновления данных игрока из Steam API.
            """
            from .models import Player
            try:
                player = Player.objects.get(id=player_id)
                if player.update_from_steam():
                    messages.success(request, f"✅ Successfully updated {player.nickname} from Steam")
                else:
                    messages.error(request, f"❌ Failed to update {player.nickname}")
            except Player.DoesNotExist:
                messages.error(request, "❌ Player not found")

            return redirect('admin:cs2_stats_player_changelist')

        custom_urls = [
            path('update-steam/<int:player_id>/',
                 self.admin_site.admin_view(update_view),
                 name='player_update_steam'),
        ]
        return custom_urls + urls


@admin.register(MonthlyStat)
class MonthlyStatAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели MonthlyStat.
    Отображает расчетные поля (K/D ratio, Win Rate).
    """
    list_display = ('player', 'year', 'month', 'matches_played', 'kd_ratio', 'win_rate')
    list_filter = ('year', 'month', 'player')  # Фильтры по году, месяцу и игроку
    search_fields = ('player__nickname',)  # Поиск по нику игрока

    # Расчетные поля только для чтения
    readonly_fields = ('kd_ratio', 'win_rate')

    # Порядок полей в форме редактирования
    fields = ('player', 'year', 'month', 'matches_played', 'kills', 'deaths', 'wins', 'kd_ratio', 'win_rate')
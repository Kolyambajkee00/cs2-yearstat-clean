from django.contrib import messages
from django.contrib import admin
from .models import Player, MonthlyStat


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'steam_id', 'country', 'cs2_hours', 'last_updated', 'update_button')
    search_fields = ('nickname', 'steam_id')
    list_filter = ('country', 'last_updated')

    # Поля для редактирования
    fields = ('steam_id', 'nickname', 'avatar', 'country', 'cs2_hours', 'last_updated')
    readonly_fields = ('last_updated',)

    # Кнопка обновления из Steam
    def update_button(self, obj):
        from django.utils.html import format_html
        return format_html(
            '<a href="update-steam/{}/" style="background: #28a745; color: white; '
            'padding: 5px 10px; border-radius: 3px; text-decoration: none; '
            'display: inline-block;">🔄 Update from Steam</a>',
            obj.id
        )

    update_button.short_description = 'Actions'

    # Добавляем кастомный URL
    def get_urls(self):
        from django.urls import path
        from django.shortcuts import redirect
        from django.contrib import messages

        urls = super().get_urls()

        def update_view(request, player_id):
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
    list_display = ('player', 'year', 'month', 'matches_played', 'kd_ratio', 'win_rate')
    list_filter = ('year', 'month', 'player')
    search_fields = ('player__nickname',)
    readonly_fields = ('kd_ratio', 'win_rate')
    fields = ('player', 'year', 'month', 'matches_played', 'kills', 'deaths', 'wins', 'kd_ratio', 'win_rate')



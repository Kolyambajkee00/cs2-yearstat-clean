from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Player, MonthlyStat
from .forms import MonthlyStatForm
from .utils.chart_utils import prepare_all_charts, calculate_total_stats


def home(request):
    """Главная страница"""
    return render(request, 'cs2_stats/home.html')


def player_search(request):
    """Поиск игрока по Steam ID"""
    if request.method == 'POST':
        steam_id = request.POST.get('steam_id', '').strip()

        if steam_id:
            # Проверяем есть ли игрок в базе
            player = Player.objects.filter(steam_id=steam_id).first()

            if player:
                return redirect('player_profile', steam_id=steam_id)
            else:
                # Создаем нового игрока
                player = Player.objects.create(steam_id=steam_id)
                # Пробуем обновить из Steam
                player.update_from_steam()
                return redirect('player_profile', steam_id=steam_id)

    return redirect('home')


def player_profile(request, steam_id):
    player = get_object_or_404(Player, steam_id=steam_id)
    monthly_stats = player.monthly_stats.all().order_by('year', 'month')

    charts = prepare_all_charts(monthly_stats)
    total_stats = calculate_total_stats(monthly_stats)

    context = {
        'player': player,
        'monthly_stats': monthly_stats,
        'charts': charts,
        'total_stats': total_stats,
    }

    return render(request, 'cs2_stats/player_profile.html', context)


def add_monthly_stat(request, steam_id):
    """Добавление статистики за месяц"""
    player = get_object_or_404(Player, steam_id=steam_id)

    if request.method == 'POST':
        # Передаем игрока в форму
        form = MonthlyStatForm(request.POST, player=player)
        if form.is_valid():
            monthly_stat = form.save(commit=False)
            monthly_stat.player = player
            monthly_stat.save()

            messages.success(
                request,
                f'✅ Statistics for {monthly_stat.year}/{monthly_stat.month} added successfully!'
            )
            return redirect('player_profile', steam_id=steam_id)
    else:
        form = MonthlyStatForm(player=player)  # ← передаем игрока

    context = {
        'player': player,
        'form': form,
        'title': f'Add Statistics for {player.nickname}'
    }
    return render(request, 'cs2_stats/add_stat.html', context)


def edit_monthly_stat(request, stat_id):
    """Редактирование статистики"""
    stat = get_object_or_404(MonthlyStat, id=stat_id)

    if request.method == 'POST':
        form = MonthlyStatForm(request.POST, instance=stat, player=stat.player)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Statistics updated successfully!')
            return redirect('player_profile', steam_id=stat.player.steam_id)
    else:
        form = MonthlyStatForm(instance=stat, player=stat.player)

    context = {
        'form': form,
        'stat': stat,
        'player': stat.player
    }
    return render(request, 'cs2_stats/edit_stat.html', context)


def delete_monthly_stat(request, stat_id):
    """Удаление статистики"""
    stat = get_object_or_404(MonthlyStat, id=stat_id)
    steam_id = stat.player.steam_id

    # Удаляем сразу (или можно добавить проверку если POST)
    stat.delete()
    messages.success(request, '✅ Statistics deleted successfully!')
    return redirect('player_profile', steam_id=steam_id)
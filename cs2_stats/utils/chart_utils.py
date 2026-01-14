import plotly.graph_objects as go
from django.utils.safestring import mark_safe
import json
import uuid


def prepare_all_charts(monthly_stats):
    """
    Создает все графики для отображения на странице профиля игрока.

    Args:
        monthly_stats (QuerySet): Набор объектов MonthlyStat для игрока

    Returns:
        list: Список HTML графиков для вставки в шаблон
              Возвращает пустой список если нет данных
    """
    charts = []

    if not monthly_stats:
        return charts

    # 1. График K/D Ratio (коэффициент убийств/смертей)
    kd_chart = create_kd_chart(monthly_stats)
    if kd_chart:
        charts.append(kd_chart)

    # 2. График Win Rate (процент побед)
    winrate_chart = create_winrate_chart(monthly_stats)
    if winrate_chart:
        charts.append(winrate_chart)

    # 3. График Kills per Match (убийств за матч)
    kpm_chart = create_kills_per_match_chart(monthly_stats)
    if kpm_chart:
        charts.append(kpm_chart)

    return charts


def create_kd_chart(monthly_stats):
    """
    Создает линейный график динамики K/D Ratio по месяцам.

    Args:
        monthly_stats (QuerySet): Статистика по месяцам

    Returns:
        str: HTML код графика или None если нет данных
    """
    months = []
    kd_values = []

    # Формируем данные для оси X (месяцы) и Y (значения K/D)
    for stat in monthly_stats:
        month_label = f"{stat.year}-{stat.month:02d}"  # Формат: "2025-01"
        months.append(month_label)
        kd_values.append(stat.kd_ratio)

    if not months:
        return None

    # Создаем линейный график Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=kd_values,
        mode='lines+markers',  # Линия + точки
        name='K/D Ratio',
        line=dict(color='blue', width=3),  # Синяя линия
        marker=dict(size=8)  # Крупные точки
    ))

    fig.update_layout(
        title='',  # Пустой заголовок (отображается в шаблоне)
        xaxis_title='Month',
        yaxis_title='K/D Ratio',
        template='plotly_white',  # Чистая белая тема
        height=400  # Фиксированная высота
    )

    return fig_to_html(fig, 'kd')


def create_winrate_chart(monthly_stats):
    """
    Создает столбчатую диаграмму процента побед по месяцам.

    Args:
        monthly_stats (QuerySet): Статистика по месяцам

    Returns:
        str: HTML код графика или None если нет данных
    """
    months = []
    winrate_values = []

    for stat in monthly_stats:
        month_label = f"{stat.year}-{stat.month:02d}"
        months.append(month_label)
        winrate_values.append(stat.win_rate)

    if not months:
        return None

    # Создаем столбчатую диаграмму
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months,
        y=winrate_values,
        name='Win Rate %',
        marker_color='green'  # Зеленые столбцы
    ))

    fig.update_layout(
        title='',
        xaxis_title='Month',
        yaxis_title='Win Rate (%)',
        template='plotly_white',
        height=400
    )

    return fig_to_html(fig, 'winrate')


def create_kills_per_match_chart(monthly_stats):
    """
    Создает график среднего количества убийств за матч по месяцам.

    Args:
        monthly_stats (QuerySet): Статистика по месяцам

    Returns:
        str: HTML код графика или None если нет данных
    """
    months = []
    kpm_values = []

    for stat in monthly_stats:
        if stat.matches_played > 0:
            month_label = f"{stat.year}-{stat.month:02d}"
            months.append(month_label)
            # Рассчитываем убийства за матч с округлением
            kpm_values.append(round(stat.kills / stat.matches_played, 1))

    if not months:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=kpm_values,
        mode='lines+markers',
        name='Kills per Match',
        line=dict(color='red', width=3),  # Красная линия
        marker=dict(size=8)
    ))

    fig.update_layout(
        title='',
        xaxis_title='Month',
        yaxis_title='Kills per Match',
        template='plotly_white',
        height=400
    )

    return fig_to_html(fig, 'kpm')


def fig_to_html(fig, chart_type):
    """
    Конвертирует объект Plotly Figure в HTML с JavaScript для отложенной загрузки.

    Args:
        fig (go.Figure): Объект графика Plotly
        chart_type (str): Тип графика ('kd', 'winrate', 'kpm')

    Returns:
        SafeString: Безопасный HTML код для вставки в шаблон Django
    """
    # Генерируем уникальный ID для div графика
    chart_id = f"{chart_type}_{uuid.uuid4().hex[:8]}"

    # Конвертируем график в JSON для передачи в JavaScript
    plot_json = fig.to_json()
    plot_data = json.loads(plot_json)

    # Создаем HTML с встроенным JavaScript для инициализации графика
    html = f'''
    <div id="{chart_id}" style="width: 100%; height: 400px;"></div>
    <script>
    // Отложенная инициализация графика (ждет загрузки Plotly библиотеки)
    function initChart_{chart_id}() {{
        if (typeof Plotly !== 'undefined') {{
            // Инициализируем график когда библиотека загружена
            Plotly.newPlot(
                '{chart_id}',
                {json.dumps(plot_data['data'])},      // Данные графика
                {json.dumps(plot_data['layout'])},    // Настройки layout
                {{"responsive": true}}                 // Адаптивность
            );
        }} else {{
            // Если Plotly ещё не загружен, повторяем через 100мс
            setTimeout(initChart_{chart_id}, 100);
        }}
    }}

    // Запускаем инициализацию когда DOM готов
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initChart_{chart_id});
    }} else {{
        initChart_{chart_id}();
    }}
    </script>
    '''

    return mark_safe(html)  # Помечаем HTML как безопасный для Django


def calculate_total_stats(monthly_stats):
    """
    Рассчитывает агрегированную статистику по всем месяцам.

    Args:
        monthly_stats (QuerySet): Статистика по месяцам

    Returns:
        dict: Словарь с общей статистикой:
            - matches: общее количество матчей
            - kills: общее количество убийств
            - deaths: общее количество смертей
            - wins: общее количество побед
            - kd: общий K/D ratio
            - win_rate: общий процент побед
    """
    total = {
        'matches': 0,
        'kills': 0,
        'deaths': 0,
        'wins': 0,
        'kd': 0,
        'win_rate': 0
    }

    if not monthly_stats:
        return total

    # Суммируем значения по всем месяцам
    for stat in monthly_stats:
        total['matches'] += stat.matches_played
        total['kills'] += stat.kills
        total['deaths'] += stat.deaths
        total['wins'] += stat.wins

    # Рассчитываем общий K/D (избегаем деления на 0)
    if total['deaths'] > 0:
        total['kd'] = round(total['kills'] / total['deaths'], 2)

    # Рассчитываем общий процент побед
    if total['matches'] > 0:
        total['win_rate'] = round((total['wins'] / total['matches']) * 100, 1)

    return total
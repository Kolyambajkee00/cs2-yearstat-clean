import plotly.graph_objects as go
from django.utils.safestring import mark_safe
import json
import uuid


def prepare_all_charts(monthly_stats):
    """Создать все графики для профиля игрока"""
    charts = []

    if not monthly_stats:
        return charts

    # 1. График K/D Ratio
    kd_chart = create_kd_chart(monthly_stats)
    if kd_chart:
        charts.append(kd_chart)  # ← Без заголовка, только график

    # 2. График Win Rate
    winrate_chart = create_winrate_chart(monthly_stats)
    if winrate_chart:
        charts.append(winrate_chart)  # ← Без заголовка

    # 3. График Kills per Match
    kpm_chart = create_kills_per_match_chart(monthly_stats)
    if kpm_chart:
        charts.append(kpm_chart)  # ← Без заголовка

    return charts


def create_kd_chart(monthly_stats):
    """Создать график K/D Ratio"""
    months = []
    kd_values = []

    for stat in monthly_stats:
        month_label = f"{stat.year}-{stat.month:02d}"
        months.append(month_label)
        kd_values.append(stat.kd_ratio)

    if not months:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=kd_values,
        mode='lines+markers',
        name='K/D Ratio',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        # УБИРАЕМ title или оставляем пустым
        title='',  # ← Пустой заголовок
        xaxis_title='Month',
        yaxis_title='K/D Ratio',
        template='plotly_white',
        height=400
    )

    return fig_to_html(fig, 'kd')


def create_winrate_chart(monthly_stats):
    """Создать график Win Rate"""
    months = []
    winrate_values = []

    for stat in monthly_stats:
        month_label = f"{stat.year}-{stat.month:02d}"
        months.append(month_label)
        winrate_values.append(stat.win_rate)

    if not months:
        return None

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months,
        y=winrate_values,
        name='Win Rate %',
        marker_color='green'
    ))

    fig.update_layout(
        title='',  # ← Пустой заголовок
        xaxis_title='Month',
        yaxis_title='Win Rate (%)',
        template='plotly_white',
        height=400
    )

    return fig_to_html(fig, 'winrate')


def create_kills_per_match_chart(monthly_stats):
    """Создать график Kills per Match"""
    months = []
    kpm_values = []

    for stat in monthly_stats:
        if stat.matches_played > 0:
            month_label = f"{stat.year}-{stat.month:02d}"
            months.append(month_label)
            kpm_values.append(round(stat.kills / stat.matches_played, 1))

    if not months:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=kpm_values,
        mode='lines+markers',
        name='Kills per Match',
        line=dict(color='red', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title='',  # ← Пустой заголовок
        xaxis_title='Month',
        yaxis_title='Kills per Match',
        template='plotly_white',
        height=400
    )

    return fig_to_html(fig, 'kpm')


def fig_to_html(fig, chart_type):
    """Конвертировать Plotly Figure в HTML с отложенной загрузкой"""
    # Генерируем уникальный ID
    chart_id = f"{chart_type}_{uuid.uuid4().hex[:8]}"

    # Конвертируем в JSON
    plot_json = fig.to_json()
    plot_data = json.loads(plot_json)

    # Создаем чистый HTML
    html = f'''
    <div id="{chart_id}" style="width: 100%; height: 400px;"></div>
    <script>
    // Отложенная инициализация графика
    function initChart_{chart_id}() {{
        if (typeof Plotly !== 'undefined') {{
            Plotly.newPlot(
                '{chart_id}',
                {json.dumps(plot_data['data'])},
                {json.dumps(plot_data['layout'])},
                {{"responsive": true}}
            );
        }} else {{
            // Если Plotly ещё не загружен, ждём
            setTimeout(initChart_{chart_id}, 100);
        }}
    }}

    // Запускаем когда DOM готов
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initChart_{chart_id});
    }} else {{
        initChart_{chart_id}();
    }}
    </script>
    '''

    return mark_safe(html)


def calculate_total_stats(monthly_stats):
    """Рассчитать общую статистику"""
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

    for stat in monthly_stats:
        total['matches'] += stat.matches_played
        total['kills'] += stat.kills
        total['deaths'] += stat.deaths
        total['wins'] += stat.wins

    if total['deaths'] > 0:
        total['kd'] = round(total['kills'] / total['deaths'], 2)

    if total['matches'] > 0:
        total['win_rate'] = round((total['wins'] / total['matches']) * 100, 1)

    return total
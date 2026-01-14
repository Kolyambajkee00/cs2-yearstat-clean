from django import template

register = template.Library()

@register.filter
def kd_badge_class(kd_ratio):
    """Вернуть класс CSS для K/D баджа"""
    if kd_ratio >= 1.2:
        return 'success'
    elif kd_ratio >= 0.8:
        return 'warning'
    else:
        return 'danger'

@register.filter
def winrate_badge_class(win_rate):
    """Вернуть класс CSS для Win Rate баджа"""
    if win_rate >= 60:
        return 'success'
    elif win_rate >= 40:
        return 'warning'
    else:
        return 'danger'
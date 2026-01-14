from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.player_search, name='player_search'),
    path('player/<str:steam_id>/', views.player_profile, name='player_profile'),
    path('player/<str:steam_id>/add-stat/', views.add_monthly_stat, name='add_monthly_stat'),
    path('stat/edit/<int:stat_id>/', views.edit_monthly_stat, name='edit_monthly_stat'),
    path('stat/delete/<int:stat_id>/', views.delete_monthly_stat, name='delete_monthly_stat'),
]
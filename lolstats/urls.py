from django.contrib import admin
from django.urls import path
from stats import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # 루트 URL에 대한 경로 설정
    path('summoner-info/', views.summoner_info, name='summoner_info'),
    path('top-players/', views.top_players, name='top_players'),
]

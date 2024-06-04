from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('summoner/', views.summoner, name='summoner'),  # 소환사 검색 결과 페이지
]

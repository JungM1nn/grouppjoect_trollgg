from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('summoner.urls')),  # 루트 경로를 summoner 앱의 URL 패턴으로 연결
]

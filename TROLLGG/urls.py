from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('summoner.urls')),  # 메인 URL에 summoner 앱 포함
    path('troll/', include('Troll_identifier.urls')),  # Troll_identifier 앱의 URL 포함
]

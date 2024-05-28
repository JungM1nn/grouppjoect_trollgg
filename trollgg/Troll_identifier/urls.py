from django.urls import path
from .views import home 

app_name = 'Troll_identifier'
urlpatterns = [
    path('', home, name='troll_identifier'),
]

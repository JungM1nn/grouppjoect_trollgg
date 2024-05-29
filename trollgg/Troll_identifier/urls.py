from django.urls import path
from . import views

urlpatterns = [
    path('', views.troll_identifier, name='troll_identifier'),
]

from django.urls import path
from .views import ejemplo_view

urlpatterns = [
    path('ejemplo/', ejemplo_view, name='ejemplo'),
]

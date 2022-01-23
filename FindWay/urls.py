from django.urls import include, path
from .views import index_view, get_data

urlpatterns = [
    path('', index_view, name="index"),
    path('way/', get_data, name = "get_data")
]
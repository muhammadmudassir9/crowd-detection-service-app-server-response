from django.urls import path
from .views import get_crowd

urlpatterns = [
    path("crowd/", get_crowd, name="get_crowd")
]

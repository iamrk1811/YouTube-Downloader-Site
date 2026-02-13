from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home_single, name="home_single"),
    path("playlist/", views.home_playlist, name="home_playlist"),
    path("playlist-ajax/", views.playlist_ajax, name="playlist_ajax"),
    path("how-to-use/", views.home_how_to_use, name="home_how_to_use"),
]

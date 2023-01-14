from django.urls import path
from . import views

urlpatterns = [
    #path("<str:name>", views.index, name = "index"),
    path("", views.home, name = "home"),
    path("movies/", views.list_movies, name = "list_movies"),
    path("show_movie/<movie_id>", views.show_movie, name = "show-movie"),

]



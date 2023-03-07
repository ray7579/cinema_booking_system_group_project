from django.urls import path
from . import views

urlpatterns = [
    #path("<str:name>", views.index, name = "index"),
    path("", views.home, name = "home"),
    path("movies/", views.list_movies, name = "list_movies"),
    path("show_movie/<movie_id>", views.show_movie, name = "show-movie"),
    path("confirmation/<movie_id>",views.confirm_movie,name = "confirm_movie"),
    path('renfilmhome/addfilm/', views.addfilm, name="addfilm"),
    path('renfilmhome/updatefilm/<movie_id>', views.updatefilm, name="updatefilm"),
    path('renfilmhome/delete/<film_id>', views.delete, name="delete"),
    path('renfilmhome/', views.renfilmhome, name = "renfilmhome"),
    path('renscreenhome/addscreen/', views.addscreen, name="addscreen"),
    path('renscreenhome/updatescreen/<screen_id>', views.updatescreen, name="updatescreen"),
    path('renscreenhome/deletescreen/<screen_id>', views.deletescreen, name="deletescreen"),
    path('renscreenhome/', views.renscreenhome, name = "renscreenhome"),

]



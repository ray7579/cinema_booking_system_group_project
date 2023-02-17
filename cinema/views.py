from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from .models import Movie, Date, Ticket

def home(response):
    user = response.user
    return render(response, "cinema/home.html", {'user': user})

def list_movies(response):
    movies = Movie.objects.all()
    return render(response, 'cinema/movies.html',{'movies': movies})

def show_movie(response, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    return render(response, 'cinema/show_movie.html',{'movie': movie})

def confirm_movie(response,movie_id):
    movie = Movie.objects.get(pk=movie_id)
    return render(response, 'cinema/confirmation.html',{'movie':movie})





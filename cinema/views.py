from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from .models import Movie, Date, Ticket
from .forms import filmForm

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

def renfilmhome(request):
    movie = Movie.objects.all()
    # if request.method == "POST":
    #     form = filmForm(request.POST or None)
    #     if form.is_valid():
    #         form.save()
    return render(request, 'cinema/home_copy.html', {'movie': movie})
    # else:
    #     return render(request, 'home.html', {'all': allFilm})


def addfilm(request):
    if request.method == "POST":
        form = filmForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renfilmhome)
    else:
        return render(request, 'cinema/addafilm.html', {})


def updatefilm(request, movie_id):
        update = Movie.objects.get(id=movie_id)
        form = filmForm(request.POST, request.FILES or None, instance=update)
        if form.is_valid():
            form.save()
            return redirect(renfilmhome)
        
        return render(request, 'cinema/updatefilm.html', {'form': form})



def delete(request, film_id):
    deleting = Movie.objects.get(id=film_id)
    deleting.delete()
    return redirect(renfilmhome)





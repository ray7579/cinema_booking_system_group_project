from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from .models import Movie, Date, Ticket, Screen, Showing
from .forms import filmForm, screenForm, showingForm
from django.contrib.auth.decorators import login_required, permission_required


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


@login_required
@permission_required("cinema.change_movie")   
def renfilmhome(request):
    movie = Movie.objects.all()
    # if request.method == "POST":
    #     form = filmForm(request.POST or None)
    #     if form.is_valid():
    #         form.save()
    return render(request, 'cinema/home_copy.html', {'movie': movie})
    # else:
    #     return render(request, 'home.html', {'all': allFilm})


@login_required
@permission_required("cinema.add_movie")
def addfilm(request):
    if request.method == "POST":
        form = filmForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renfilmhome)
    else:
        return render(request, 'cinema/addafilm.html', {})


@login_required
@permission_required("cinema.change_movie")
def updatefilm(request, movie_id):
        update = Movie.objects.get(id=movie_id)
        form = filmForm(request.POST, request.FILES or None, instance=update)
        if form.is_valid():
            form.save()
            return redirect(renfilmhome)
        
        return render(request, 'cinema/updatefilm.html', {'form': form})


@login_required
@permission_required("cinema.delete_movie")
def delete(request, film_id):
    deleting = Movie.objects.get(id=film_id)
    deleting.delete()
    return redirect(renfilmhome)


@login_required
def renscreenhome(request):
    screen = Screen.objects.all()
    # if request.method == "POST":
    #     form = filmForm(request.POST or None)
    #     if form.is_valid():
    #         form.save()
    return render(request, 'cinema/cinman_screen.html', {'screen': screen})
    # else:
    #     return render(request, 'home.html', {'all': allFilm})


@login_required
def addscreen(request):
    if request.method == "POST":
        form = screenForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renscreenhome)
    else:
        return render(request, 'cinema/addascreen.html', {})


@login_required
def updatescreen(request, screen_id):
        update = Screen.objects.get(id=screen_id)
        form = screenForm(request.POST, request.FILES or None, instance=update)
        if form.is_valid():
            form.save()
            return redirect(renscreenhome)
        
        return render(request, 'cinema/updatescreen.html', {'form': form})


@login_required
def deletescreen(request, screen_id):
    deleting = Screen.objects.get(id=screen_id)
    deleting.delete()
    return redirect(renscreenhome)
    
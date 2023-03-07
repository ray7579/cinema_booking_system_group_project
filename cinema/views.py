from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from .models import Movie, Date, Ticket, Screen, Showing
from .forms import filmForm, screenForm, showingForm

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


def renscreenhome(request):
    screen = Screen.objects.all()
    # if request.method == "POST":
    #     form = filmForm(request.POST or None)
    #     if form.is_valid():
    #         form.save()
    return render(request, 'cinema/cinman_screen.html', {'screen': screen})
    # else:
    #     return render(request, 'home.html', {'all': allFilm})


def addscreen(request):
    if request.method == "POST":
        form = screenForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renscreenhome)
    else:
        return render(request, 'cinema/addascreen.html', {})


def updatescreen(request, screen_id):
        update = Screen.objects.get(id=screen_id)
        form = screenForm(request.POST, request.FILES or None, instance=update)
        if form.is_valid():
            form.save()
            return redirect(renscreenhome)
        
        return render(request, 'cinema/updatescreen.html', {'form': form})



def deletescreen(request, screen_id):
    deleting = Screen.objects.get(id=screen_id)
    deleting.delete()
    return redirect(renscreenhome)

def renshowhome(request):
    showing = Showing.objects.all()
    # if request.method == "POST":
    #     form = filmForm(request.POST or None)
    #     if form.is_valid():
    #         form.save()
    return render(request, 'cinema/cinman_show.html', {'showing': showing})
    # else:
    #     return render(request, 'home.html', {'all': allFilm})


def addshow(request):
    if request.method == "POST":
        form = showingForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renshowhome)
    else:
        return render(request, 'cinema/addashow.html', {})


def updateshow(request, showing_id):
        update = Showing.objects.get(id=showing_id)
        form = showingForm(request.POST, request.FILES or None, instance=update)
        if form.is_valid():
            form.save()
            return redirect(renshowhome)
        
        return render(request, 'cinema/updateshow.html', {'form': form})



def deleteshow(request, showing_id):
    deleting = Showing.objects.get(id=showing_id)
    deleting.delete()
    return redirect(renshowhome)
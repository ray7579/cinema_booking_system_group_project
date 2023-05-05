from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from .models import Movie, Screen, Showing, TicketPrice
from .forms import filmForm, screenForm, showingForm, BookingForm, Booking
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
# from django.core.exceptions import ProtectedError
import messages
from django.urls import reverse
from django.core.exceptions import ValidationError




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


def showings_list(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    showings = Showing.objects.filter(film=movie)
    return render(request, 'cinema/showings_list.html', {'movie': movie, 'showings': showings})


def calculate_total_price(booking, ticket_prices):
    total_price = 0
    total_price += booking.child_tickets * ticket_prices.child
    total_price += booking.student_tickets * ticket_prices.student
    total_price += booking.adult_tickets * ticket_prices.adult
    return total_price

def book_showing(request, showing_id):
    showing = get_object_or_404(Showing, pk=showing_id)
    ticket_prices = TicketPrice.objects.first()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.showing = showing
            #calculate the total price and assign it to the booking
            booking.total_price = calculate_total_price(booking, ticket_prices)

            #check if there are enough tickets available
            available_tickets = showing.screen.capacity - showing.tickets_sold
            if booking.child_tickets + booking.student_tickets + booking.adult_tickets > available_tickets:
                raise ValidationError('Not enough tickets available')
            
            #update the tickets_sold attribute of the showing
            showing.tickets_sold += booking.child_tickets + booking.student_tickets + booking.adult_tickets
            showing.save()
            booking.save()
            return redirect('booking_success', booking_id=booking.id)
    else:
        form = BookingForm()

    form_elements = {
        ticket_type: {
            'label': form[ticket_type + '_tickets'].label_tag,
            'field': form[ticket_type + '_tickets'],
            'initial': form.initial.get(ticket_type + '_tickets', 0),
        }
        for ticket_type in ['child', 'student', 'adult']
    }

    context = {
        'showing': showing,
        'form': form,
        'form_elements': form_elements,
        'ticket_prices': ticket_prices,
    }
    return render(request, 'cinema/book_showing.html', context)



def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, 'cinema/booking_success.html', {'booking': booking})







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
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        form = filmForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            form.save()
            return redirect('renfilmhome')
    else:
        form = filmForm(instance=movie)
    return render(request, 'cinema/updatefilm.html', {'form': form, 'movie': movie})



@login_required
@permission_required("cinema.delete_movie")
def delete(request, film_id):

    deleting = get_object_or_404(Movie, id=film_id)
    showing = Showing.objects.filter(film=deleting)
    if showing.exists():
        return redirect(list_movies)
    else:
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
        screen = get_object_or_404(Screen, id=screen_id)
        form = screenForm(request.POST or None, instance=screen)
        if form.is_valid():
            form.save()
            return redirect(renscreenhome)
        
        return render(request, 'cinema/updatescreen.html', {'form': form, 'screen': screen})


@login_required
def deletescreen(request, screen_id):

    deleting = get_object_or_404(Screen, id=screen_id)
    showing = Showing.objects.filter(screen=deleting)
    if showing.exists():
        return redirect(list_movies)
    else:
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

def renaddshow(request):
    film = Movie.objects.all()
    screen = Screen.objects.all()
    # if request.method == "POST":
    #     form = filmForm(request.POST or None)
    #     if form.is_valid():
    #         form.save()
    return render(request, 'cinema/addashow.html', {'film': film, 'screen' : screen})

def addshow(request):
    if request.method == "POST":
        # film = Movie.objects.all()
        # screen = Screen.objects.all()
        form = showingForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renshowhome)
    else:
        return render(request, 'cinema/addashow.html', {})




def updateshow(request, showing_id):
        film = Movie.objects.all()
        screen = Screen.objects.all()
        update = Showing.objects.get(id=showing_id)
        form = showingForm(request.POST, request.FILES or None, instance=update)
        if form.is_valid():
            form.save()
            return redirect(renshowhome)
        
        return render(request, 'cinema/updateshow.html', {'form': form, 'film': film, 'screen' : screen})



def deleteshow(request, showing_id):
    deleting = Showing.objects.get(id=showing_id)
    deleting.delete()
    return redirect(renshowhome)

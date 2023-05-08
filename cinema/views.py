from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from .models import Movie, Screen, Showing, TicketPrice
from .forms import filmForm, screenForm, showingForm, BookingForm, Booking, StudentBookingForm
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
# from django.core.exceptions import ProtectedError
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta, datetime
import messages
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


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
    current_datetime = timezone.now()
    showings = Showing.objects.filter(film=movie, date__gte=current_datetime.date()).order_by('date', 'time')
    showings = [showing for showing in showings if not (showing.date == current_datetime.date() and showing.time < current_datetime.time())]
    return render(request, 'cinema/showings_list.html', {'movie': movie, 'showings': showings})


def calculate_total_price(booking, ticket_prices):
    total_price = 0
    total_price += booking.child_tickets * ticket_prices.child
    total_price += booking.student_tickets * ticket_prices.student
    total_price += booking.adult_tickets * ticket_prices.adult
    return total_price

def book_showing(request, showing_id):
    showing = get_object_or_404(Showing, pk=showing_id)
    current_datetime = timezone.now()
    showing_datetime = datetime.combine(showing.date, showing.time, tzinfo=current_datetime.tzinfo)
    one_minute_before_showing = showing_datetime - timedelta(minutes=1)

    if current_datetime >= one_minute_before_showing:
        error_message = 'Booking is not allowed within 1 minute of the showtime'
        return render(request, 'cinema/book_showing.html', {'error_message': error_message, 'showing': showing})

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
                error_message = 'Not enough tickets available'
                return render(request, 'cinema/book_showing.html', {'error_message': error_message, 'showing': showing})

            #create a Stripe charge
            token = request.POST.get('stripeToken')
            amount = int(booking.total_price * 100)  # Convert total price to cents
            try:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency='gbp',
                    description='Cinema Ticket Booking',
                    source=token,
                )

                #update the tickets_sold attribute of the showing
                showing.tickets_sold += booking.child_tickets + booking.student_tickets + booking.adult_tickets
                showing.save()
                booking.save()

                return redirect('booking_success', booking_id=booking.id)

            except stripe.error.CardError as e:
                #if declined payment
                body = e.json_body
                err = body.get('error', {})
                error_message = f"Payment declined: {err.get('message')}"
                return render(request, 'cinema/book_showing.html', {'error_message': error_message, 'showing': showing})

            except stripe.error.StripeError as e:
                # if stripe errors
                error_message = "An error occurred while processing your payment. Please try again."
                return render(request, 'cinema/book_showing.html', {'error_message': error_message})

            except Exception as e:
                # srtipe errors
                error_message = "An unexpected error occurred. Please try again."
                return render(request, 'cinema/book_showing.html', {'error_message': error_message})
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
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'cinema/book_showing.html', context)



def student_book_showing(request, showing_id):
    showing = get_object_or_404(Showing, pk=showing_id)
    current_datetime = timezone.now()
    showing_datetime = datetime.combine(showing.date, showing.time, tzinfo=current_datetime.tzinfo)
    one_minute_before_showing = showing_datetime - timedelta(minutes=1)

    if current_datetime >= one_minute_before_showing:
        error_message = 'Booking is not allowed within 1 minute of the showtime'
        return render(request, 'cinema/book_showing.html', {'error_message': error_message, 'showing': showing})

    ticket_prices = TicketPrice.objects.first()
    if request.method == 'POST':
        form = StudentBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.showing = showing

            #save the logged-in user's account to the booking
            if request.user.is_authenticated:
                booking.user = request.user
                booking.email = request.user.email

            #calculate the total price and assign it to the booking
            booking.total_price = calculate_total_price(booking, ticket_prices)

            #check if there are enough tickets available
            available_tickets = showing.screen.capacity - showing.tickets_sold
            if booking.child_tickets + booking.student_tickets + booking.adult_tickets > available_tickets:
                error_message = 'Not enough tickets available'
                return render(request, 'cinema/book_showing.html', {'error_message': error_message, 'showing': showing})

            #create a Stripe charge
            token = request.POST.get('stripeToken')
            amount = int(booking.total_price * 100)  # Convert total price to cents
            try:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency='gbp',
                    description='Cinema Ticket Booking',
                    source=token,
                )

                #update the tickets_sold attribute of the showing
                showing.tickets_sold += booking.child_tickets + booking.student_tickets + booking.adult_tickets
                showing.save()
                booking.save()

                return redirect('booking_success', booking_id=booking.id)

            except stripe.error.CardError as e:
                #if declined payment
                body = e.json_body
                err = body.get('error', {})
                error_message = f"Payment declined: {err.get('message')}"
                return render(request, 'cinema/book_showing.html', {'error_message': error_message, 'showing': showing})

            except stripe.error.StripeError as e:
                # if stripe errors
                error_message = "An error occurred while processing your payment. Please try again."
                return render(request, 'cinema/book_showing.html', {'error_message': error_message})

            except Exception as e:
                # srtipe errors
                error_message = "An unexpected error occurred. Please try again."
                return render(request, 'cinema/book_showing.html', {'error_message': error_message})
    else:
        form = StudentBookingForm()

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
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'cinema/student_book_showing.html', context)


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, 'cinema/booking_success.html', {'booking': booking})


def not_enough_tickets(request):
    return render(request, 'cinema/not_enough_tickets.html')


@login_required
@permission_required("cinema.change_movie")   
def renfilmhome(request):
    movie = Movie.objects.all()
    return render(request, 'cinema/home_copy.html', {'movie': movie})


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
@permission_required("cinema.change_movie")   
def renscreenhome(request):
    screen = Screen.objects.all()
    return render(request, 'cinema/cinman_screen.html', {'screen': screen})


@login_required
@permission_required("cinema.change_movie")   
def addscreen(request):
    if request.method == "POST":
        form = screenForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renscreenhome)
    else:
        return render(request, 'cinema/addascreen.html', {})


@login_required
@permission_required("cinema.change_movie")   
def updatescreen(request, screen_id):
        screen = get_object_or_404(Screen, id=screen_id)
        form = screenForm(request.POST or None, instance=screen)
        if form.is_valid():
            form.save()
            return redirect(renscreenhome)
        
        return render(request, 'cinema/updatescreen.html', {'form': form, 'screen': screen})


@login_required
@permission_required("cinema.change_movie")   
def deletescreen(request, screen_id):

    deleting = get_object_or_404(Screen, id=screen_id)
    showing = Showing.objects.filter(screen=deleting)
    if showing.exists():
        return redirect(list_movies)
    else:
        deleting.delete()
        return redirect(renscreenhome)


@login_required
@permission_required("cinema.change_movie")   
def renshowhome(request):
    showing = Showing.objects.all().order_by('date', 'time')
    return render(request, 'cinema/cinman_show.html', {'showing': showing})


@login_required
@permission_required("cinema.change_movie")   
def renaddshow(request):
    film = Movie.objects.all()
    screen = Screen.objects.all()
    return render(request, 'cinema/addashow.html', {'film': film, 'screen' : screen})


@login_required
@permission_required("cinema.change_movie")   
def addshow(request):
    if request.method == "POST":
        form = showingForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renshowhome)
    else:
        return render(request, 'cinema/addashow.html', {})


@login_required
@permission_required("cinema.change_movie")   
def updateshow(request, showing_id):
        film = Movie.objects.all()
        screen = Screen.objects.all()
        update = Showing.objects.get(id=showing_id)
        form = showingForm(request.POST, request.FILES or None, instance=update)
        if form.is_valid():
            form.save()
            return redirect(renshowhome)
        
        return render(request, 'cinema/updateshow.html', {'form': form, 'film': film, 'screen' : screen})


@login_required
@permission_required("cinema.change_movie")   
def deleteshow(request, showing_id):
    deleting = Showing.objects.get(id=showing_id)
    deleting.delete()
    return redirect(renshowhome)

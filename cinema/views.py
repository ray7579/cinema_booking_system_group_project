from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Screen, Showing, TicketPrice
from .forms import filmForm, screenForm, showingForm, BookingForm, Booking, StudentBookingForm, ClubRepBookingForm
from django.contrib.auth.decorators import login_required, permission_required
#from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta, datetime
import messages
import stripe
import qrcode
from sib_api_v3_sdk.api import TransactionalEmailsApi
from sib_api_v3_sdk import Configuration, SendSmtpEmail, ApiClient
import base64
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from sib_api_v3_sdk.rest import ApiException
from accounts.models import User
from django.db.models.functions import TruncMonth
from django.db.models import Count
from decimal import Decimal
from django.contrib.auth.decorators import user_passes_test

stripe.api_key = settings.STRIPE_SECRET_KEY



def is_accountmanager(user):
    return user.is_authenticated and user.is_accountmanager

def is_cinemamanager(user):
    return user.is_authenticated and user.is_cinemamanager

def is_student(user):
    return user.is_authenticated and user.is_student

def is_clubrep(user):
    return user.is_authenticated and user.is_clubrep








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



def calculate_total_price(booking, ticket_prices, is_clubrep):
    total_price = Decimal('0.00')
    total_price += booking.child_tickets * ticket_prices.child
    total_price += booking.student_tickets * ticket_prices.student
    total_price += booking.adult_tickets * ticket_prices.adult
    if is_clubrep:
        discount = Decimal('0.1')
        total_price *= (Decimal('1.00') - discount)
    return total_price.quantize(Decimal('.01'))



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

            if request.user.is_authenticated:
                is_clubrep = request.user.is_clubrep
            else:
                is_clubrep = False


            #calculate the total price and assign it to the booking
            booking.total_price = calculate_total_price(booking, ticket_prices, is_clubrep)

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


@user_passes_test(is_student)
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
                is_clubrep = request.user.is_clubrep

            #calculate the total price and assign it to the booking
            booking.total_price = calculate_total_price(booking, ticket_prices, is_clubrep)

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



@user_passes_test(is_clubrep)
def club_rep_book_showing(request, showing_id):
    showing = get_object_or_404(Showing, pk=showing_id)
    current_datetime = timezone.now()
    showing_datetime = datetime.combine(showing.date, showing.time, tzinfo=current_datetime.tzinfo)
    one_minute_before_showing = showing_datetime - timedelta(minutes=1)

    if current_datetime >= one_minute_before_showing:
        error_message = 'Booking is not allowed within 1 minute of the showtime'
        return render(request, 'cinema/club_rep_book_showing.html', {'error_message': error_message, 'showing': showing})

    ticket_prices = TicketPrice.objects.first()
    if request.method == 'POST':
        form = ClubRepBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.showing = showing

            #add your logic here for handling the Club Rep booking submission

            #save the logged-in user's account to the booking
            if request.user.is_authenticated:
                booking.user = request.user
                booking.email = request.user.email
                is_clubrep = request.user.is_clubrep

            #calculate the total price and assign it to the booking
            booking.total_price = calculate_total_price(booking, ticket_prices, is_clubrep)

            #check if there are enough tickets available
            available_tickets = showing.screen.capacity - showing.tickets_sold
            if booking.student_tickets > available_tickets:
                error_message = 'Not enough tickets available'
                return render(request, 'cinema/club_rep_book_showing.html', {'error_message': error_message, 'showing': showing})

            #add your payment processing logic here

            #update the tickets_sold attribute of the showing
            showing.tickets_sold += booking.student_tickets
            showing.save()
            booking.save()

            return redirect('booking_success', booking_id=booking.id)
    else:
        form = ClubRepBookingForm()

    form_elements = {
        ticket_type: {
            'label': form[ticket_type + '_tickets'].label_tag,
            'field': form[ticket_type + '_tickets'],
            'initial': form.initial.get(ticket_type + '_tickets', 0),
        }
        for ticket_type in ['student']
    }

    context = {
        'showing': showing,
        'form': form,
        'form_elements': form_elements,
        'ticket_prices': ticket_prices,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'cinema/club_rep_book_showing.html', context)




def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    #generate QR code
    qr_data = f"Booking ID: {booking.id}, Movie: {booking.showing.film.name}, Screen: {booking.showing.screen.number}, Date: {booking.showing.date}, Time: {booking.showing.time}"
    qr_image = qrcode.make(qr_data)

    #save QR code to a temporary file
    temp_file = NamedTemporaryFile()
    qr_image.save(temp_file, format='PNG')
    temp_file.flush()

    #save the temporary file to the booking object
    booking.qr_code.save(f"qr_code_{booking.id}.png", File(temp_file))
    booking.save()

    #send the booking email
    send_booking_email(booking)

    return render(request, 'cinema/booking_success.html', {'booking': booking})


def not_enough_tickets(request):
    return render(request, 'cinema/not_enough_tickets.html')


@user_passes_test(is_accountmanager)
def booking_history(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    bookings = Booking.objects.filter(user=user)
    return render(request, 'cinema/booking_history.html', {'user': user, 'bookings': bookings})



@user_passes_test(is_cinemamanager)   
def renfilmhome(request):
    movie = Movie.objects.all()
    return render(request, 'cinema/home_copy.html', {'movie': movie})


@user_passes_test(is_cinemamanager)
def addfilm(request):
    if request.method == "POST":
        form = filmForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renfilmhome)
    else:
        return render(request, 'cinema/addafilm.html', {})


@user_passes_test(is_cinemamanager)
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



@user_passes_test(is_cinemamanager)
def delete(request, film_id):

    deleting = get_object_or_404(Movie, id=film_id)
    showing = Showing.objects.filter(film=deleting)
    if showing.exists():
        return redirect(list_movies)
    else:
        deleting.delete()
        return redirect(renfilmhome)


@user_passes_test(is_cinemamanager)
def renscreenhome(request):
    screen = Screen.objects.all()
    return render(request, 'cinema/cinman_screen.html', {'screen': screen})


@user_passes_test(is_cinemamanager)
def addscreen(request):
    if request.method == "POST":
        form = screenForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renscreenhome)
    else:
        return render(request, 'cinema/addascreen.html', {})


@user_passes_test(is_cinemamanager)  
def updatescreen(request, screen_id):
        screen = get_object_or_404(Screen, id=screen_id)
        form = screenForm(request.POST or None, instance=screen)
        if form.is_valid():
            form.save()
            return redirect(renscreenhome)
        
        return render(request, 'cinema/updatescreen.html', {'form': form, 'screen': screen})


@user_passes_test(is_cinemamanager)  
def deletescreen(request, screen_id):

    deleting = get_object_or_404(Screen, id=screen_id)
    showing = Showing.objects.filter(screen=deleting)
    if showing.exists():
        return redirect(list_movies)
    else:
        deleting.delete()
        return redirect(renscreenhome)


@user_passes_test(is_cinemamanager)  
def renshowhome(request):
    showing = Showing.objects.all().order_by('date', 'time')
    return render(request, 'cinema/cinman_show.html', {'showing': showing})


@user_passes_test(is_cinemamanager)
def renaddshow(request):
    film = Movie.objects.all()
    screen = Screen.objects.all()
    return render(request, 'cinema/addashow.html', {'film': film, 'screen' : screen})


@user_passes_test(is_cinemamanager)
def addshow(request):
    if request.method == "POST":
        form = showingForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
        return redirect(renshowhome)
    else:
        return render(request, 'cinema/addashow.html', {})


@user_passes_test(is_cinemamanager)  
def updateshow(request, showing_id):
        film = Movie.objects.all()
        screen = Screen.objects.all()
        update = Showing.objects.get(id=showing_id)
        form = showingForm(request.POST, request.FILES or None, instance=update)
        if form.is_valid():
            form.save()
            return redirect(renshowhome)
        
        return render(request, 'cinema/updateshow.html', {'form': form, 'film': film, 'screen' : screen})


@user_passes_test(is_cinemamanager)  
def deleteshow(request, showing_id):
    deleting = Showing.objects.get(id=showing_id)
    deleting.delete()
    return redirect(renshowhome)


def send_booking_email(booking):
    configuration = Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = TransactionalEmailsApi(ApiClient(configuration))

    #include the QR code as an attachment
    qr_code_file_path = booking.qr_code.path
    with open(qr_code_file_path, "rb") as f:
        qr_code_content = f.read()

    #encode the QR code content as base64
    qr_code_base64 = base64.b64encode(qr_code_content).decode('utf-8')

    email_data = SendSmtpEmail(
        to=[{"email": booking.email}],
        sender={"email": "info.uweflixcinema@gmail.com", "name": "UWEFlix Cinema"},
        subject="Booking Confirmation",
        html_content = f'''
        <p>Thank you for booking tickets at our cinema. Please find your booking details and QR code below.</p>
        <p><strong>Movie:</strong> {booking.showing.film.name}</p>
        <p><strong>Screen:</strong> {booking.showing.screen.number}</p>
        <p><strong>Date:</strong> {booking.showing.date}</p>
        <p><strong>Time:</strong> {booking.showing.time}</p>
        <img src="data:image/png;base64,{qr_code_base64}">
        '''
    )

    #attach the QR code as an attachment
    email_data.attachments = [{
        "name": f"qr_code_{booking.id}.png",
        "content": qr_code_base64
    }]

    try:
        api_instance.send_transac_email(email_data)
    except ApiException as e:
        print(f"An error occurred while sending the email: {e}")



@user_passes_test(is_accountmanager)
def booking_month_select(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    bookings = user.bookings.all()
    months = set((booking.showing.date.year, booking.showing.date.month) for booking in bookings)
    return render(request, 'cinema/booking_month_select.html', {'user': user, 'months': months})

@user_passes_test(is_accountmanager)
def booking_month_view(request, user_id, year, month):
    user = get_object_or_404(User, pk=user_id)
    bookings = user.bookings.filter(showing__date__year=year, showing__date__month=month)
    total_spent = Decimal(sum(booking.total_price for booking in bookings))
    return render(request, 'cinema/booking_month_view.html', {
        'user': user,
        'bookings': bookings,
        'total_spent': total_spent,
        'year': year,
        'month': month
    })

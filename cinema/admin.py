from django.contrib import admin
from .models import Movie, Showing, Screen, Booking, TicketPrice


admin.site.register(Movie)
admin.site.register(Showing)
admin.site.register(Screen)
admin.site.register(Booking)
admin.site.register(TicketPrice)



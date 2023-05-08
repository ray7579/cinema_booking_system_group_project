from django.urls import path
from .import views

urlpatterns=[
    path('', views.home, name='home'),
    path("movies/", views.list_movies, name = "list_movies"),
    path("show_movie/<movie_id>", views.show_movie, name = "show_movie"),
    path('showings_list/<int:movie_id>/', views.showings_list, name='showings_list'),
    path('book_showing/<int:showing_id>/', views.book_showing, name='book_showing'),
    path('student_book_showing/<int:showing_id>/', views.student_book_showing, name='student_book_showing'),
    path('club_rep_book_showing/<int:showing_id>/', views.club_rep_book_showing, name='club_rep_book_showing'),
    path('booking_success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('not_enough_tickets/', views.not_enough_tickets, name='not_enough_tickets'),
    path('accountslist/bookinghistory/<int:user_id>/', views.booking_history, name='booking_history'),
    #path('ticket_booking/<int:showing_id>/', views.ticket_booking_view, name='ticket_booking_view'),
    #path("success/<int:ticket_id>/", views.success_view, name="success_view"),  # Updated this line
    path('renfilmhome/addfilm/', views.addfilm, name="addfilm"),
    path('renfilmhome/updatefilm/<movie_id>', views.updatefilm, name="updatefilm"),
    path('renfilmhome/delete/<film_id>', views.delete, name="delete"),
    path('renfilmhome/', views.renfilmhome, name = "renfilmhome"),
    path('renscreenhome/addscreen/', views.addscreen, name="addscreen"),
    path('renscreenhome/updatescreen/<screen_id>', views.updatescreen, name="updatescreen"),
    path('renscreenhome/deletescreen/<screen_id>', views.deletescreen, name="deletescreen"),
    path('renscreenhome/', views.renscreenhome, name = "renscreenhome"),
    path('renshowhome/renaddshow/', views.renaddshow, name="renaddshow"),
    path('renshowhome/renaddshow/addshow/', views.addshow, name="addshow"),
    path('renshowhome/updateshow/<showing_id>', views.updateshow, name="updateshow"),
    path('renshowhome/deleteshow/<showing_id>', views.deleteshow, name="deleteshow"),
    path('renshowhome/', views.renshowhome, name = "renshowhome"),
]



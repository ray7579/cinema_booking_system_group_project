from django.urls import path
from . import views

app_name = 'ticket_booking'

urlpatterns = [
    path('ticket', views.ticket_booking_view, name='ticket_booking'),
    path('success/<int:ticket_id>/', views.success_view, name='success'),
]

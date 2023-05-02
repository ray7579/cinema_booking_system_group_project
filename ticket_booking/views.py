from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.core.validators import RegexValidator
from .models import Ticket

class TicketBookingForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(validators=[RegexValidator(regex='^((\+44\s?\d{4}|\(?\d{4}\)?)\s?\d{3}\s?\d{3})|(\+44\d{10})$', message='Invalid UK Phone Number')])

    ticket_type_choices = (
        ('student', 'Student'),
        ('child', 'Child'),
        ('adult', 'Adult'),
    )
    ticket_type = forms.ChoiceField(choices=ticket_type_choices, widget=forms.RadioSelect(attrs={'class': 'ticket-type'}))
    ticket_quantity = forms.IntegerField(initial=1, min_value=1, widget=forms.NumberInput(attrs={'class': 'ticket-quantity'}))

def ticket_booking_view(request):
    if request.method == 'POST':
        form = TicketBookingForm(request.POST)
        if form.is_valid():
            # Check screen capacity
            print("valid-----------")
            ticket_quantity = form.cleaned_data['ticket_quantity']
            if ticket_quantity > 80:
                return render(request, 'ticket_booking/booking_error.html', {'error_message': 'Screen capacity is 80. Please reduce the number of tickets.'})
            
            # Calculate total price
            ticket_type = form.cleaned_data['ticket_type']
            ticket_price = 0
            if ticket_type == 'student':
                ticket_price = 8.50
            elif ticket_type == 'child':
                ticket_price = 6.50
            elif ticket_type == 'adult':
                ticket_price = 11
            total_price = ticket_price * ticket_quantity
            
            # Save ticket object
            ticket = Ticket(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                ticket_type=ticket_type,
                ticket_quantity=ticket_quantity,
                ticket_price=ticket_price,
                total_price=total_price,
            )
            ticket.save()
            
            # Redirect to success page
            return redirect('ticket_booking:success', ticket_id=ticket.id)
    else:
        form = TicketBookingForm()
    return render(request, 'ticket_booking/ticket_booking.html', {'form': form})

def success_view(request, ticket_id):
    # Retrieve ticket object from database
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    return render(request, 'ticket_booking/success.html', {'ticket': ticket})

from django import forms
from django.core.validators import RegexValidator
from .models import Ticket

class TicketBookingForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=14, validators=[RegexValidator(regex='^(\+44|0)\d{10}$', message='Invalid UK Phone Number')])

    TICKET_TYPE_CHOICES = (
        ('student', 'Student'),
        ('child', 'Child'),
        ('adult', 'Adult'),
    )
    ticket_type = forms.ChoiceField(choices=TICKET_TYPE_CHOICES, widget=forms.RadioSelect(attrs={'class': 'ticket-type'}))
    ticket_quantity = forms.IntegerField(initial=1, min_value=1, widget=forms.NumberInput(attrs={'class': 'ticket-quantity'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Ticket.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and Ticket.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('This phone number is already in use.')
        return phone_number

    def __init__(self, *args, **kwargs):
        self.screening = kwargs.pop('screening')
        super().__init__(*args, **kwargs)

    def clean_ticket_quantity(self):
        ticket_quantity = self.cleaned_data['ticket_quantity']
        if ticket_quantity > self.screening.get_available_seats():
            raise forms.ValidationError(f'There are only {self.screening.get_available_seats()} tickets available for this screening.')

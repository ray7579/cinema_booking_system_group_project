from django import forms
from .models import Movie
from .models import Screen
from .models import Showing

class filmForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['name', 'description', 'age_rating', 'duration','image']

class screenForm(forms.ModelForm):
    class Meta:
        model = Screen
        fields = ['number', 'capacity']

class showingForm(forms.ModelForm):
    class Meta:
        model = Showing
        fields = ['film', 'screen', 'date', 'time']

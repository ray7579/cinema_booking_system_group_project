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

# class showingForm(forms.ModelForm):
#     class Meta:
#         model = Showing
#         fields = ['film', 'screen', 'date', 'time']
#         film = forms.ModelChoiceField(queryset=Movie.objects.all())
#         screen = forms.ModelChoiceField(queryset=Screen.objects.all())

class showingForm(forms.ModelForm):
    class Meta:
        model = Showing
        fields = ['film', 'screen', 'date', 'time']
        widgets = {
            'film': forms.Select(attrs={'class': 'form-control'}),
            'screen': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'class': 'form-control'}),
        }

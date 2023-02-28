from django import forms
from .models import Movie

class filmForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['name', 'description', 'age_rating', 'duration','image']
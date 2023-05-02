from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User, Student,AccountManager,CinemaManager,ClubRep
from django.db import transaction
from django.contrib.auth.models import Group


class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        student = Student.objects.create(user=user)
        student.save()
        return student  

    
    
class ClubRepSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    clubname = forms.CharField(required=True)
    street_no = forms.IntegerField(required=True)
    street = forms.CharField(required=True)
    city = forms.CharField(required=True)
    postcode = forms.CharField(required=True)
    landline_no = forms.CharField(required=True)
    mobile_no = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_clubrep = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        clubrep = ClubRep.objects.create(user=user)
        clubrep.clubname = self.cleaned_data.get('clubname')
        clubrep.street_no = self.cleaned_data.get('street_no')
        clubrep.street = self.cleaned_data.get('street')
        clubrep.city = self.cleaned_data.get('city')
        clubrep.postcode = self.cleaned_data.get('postcode')
        clubrep.landline_no = self.cleaned_data.get('landline_no')
        clubrep.mobile_no = self.cleaned_data.get('mobile_no')
        clubrep.save()
        return clubrep
    
class CinemamanagerSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_cinemamanager = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        manager = CinemaManager.objects.create(user=user)
        manager.save()
        group = Group.objects.get(name='cinema_manager')
        user.groups.add(group)
        return manager  
    
class AccountmanagerSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_accountmanager = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        manager = AccountManager.objects.create(user=user)
        manager.save()
        group = Group.objects.get(name='account_manager')
        user.groups.add(group)
        return manager  


class userForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['credit']

class ClubrepUpdateForm(forms.ModelForm):
    class Meta:
        model = ClubRep
        fields = ['clubname', 'street_no', 'street', 'city', 'postcode', 'landline_no', 'mobile_no', 'credit']


class AccountmanagerUpdateForm(forms.ModelForm):
    class Meta:
        model = AccountManager
        fields = '__all__'
      

class CinemamanagerUpdateForm(forms.ModelForm):
    class Meta:
        model = CinemaManager
        fields = '__all__'





    
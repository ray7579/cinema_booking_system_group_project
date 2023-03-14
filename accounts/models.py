from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal



class User(AbstractUser):
    is_accountmanager= models.BooleanField(default=False)
    is_cinemamanager = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_clubrep = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    

class CinemaManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

class AccountManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

class ClubRep(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    clubname = models.CharField(max_length=50)
    street_no = models.IntegerField(default=0)
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10)
    landline_no = models.CharField(max_length=20)
    mobile_no = models.CharField(max_length=20)
    credit = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    credit = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(max_length=20)
    
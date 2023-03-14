from django.contrib import admin
from .models import User, CinemaManager,AccountManager, Student, ClubRep, Customer

# Register your models here.

admin.site.register(User)
admin.site.register(CinemaManager)
admin.site.register(AccountManager)
admin.site.register(Student)
admin.site.register(ClubRep)
admin.site.register(Customer)   
from django.db import models

# Create your models here.

class Movie(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(null=True, max_length=500)
    age_rating = models.CharField(null=True, max_length=50)
    image = models.ImageField(upload_to='covers/', null=True)

    def __str__(self):
        return self.name


class Date(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.CharField(max_length=50)
    capacity = models.IntegerField(default=50)

    def __str__(self):
        return '%s %s' % (self.date, self.time)

#class Time(models.Model):
#    dates = models.ForeignKey(Date, on_delete=models.CASCADE)
#    time = models.CharField(max_length=50)
#
#    def __str__(self):
#        return self.time


#class Capacity
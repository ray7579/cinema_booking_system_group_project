from django.db import models
from django.core.validators import MaxValueValidator


class Movie(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(null=True, max_length=1000)
    age_rating = models.IntegerField(null=True, validators=[MaxValueValidator(18)])
    duration = models.IntegerField( null=True, validators=[MaxValueValidator(240)])
    image = models.ImageField(upload_to='covers/', null=True)

    def __str__(self):
        return self.name


class Screen(models.Model):
    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(validators=[MaxValueValidator(300)])
    
    def __str__(self):
        return str(self.number) #, str(self.capacity)


class Showing(models.Model):
    film = models.ForeignKey(Movie, on_delete=models.PROTECT)
    screen = models.ForeignKey(Screen, on_delete=models.PROTECT)
    date = models.DateField()
    time = models.TimeField()
    covid = models.BooleanField(default=False)
    tickets_sold = models.PositiveIntegerField(default=0)
        
    def __str__(self):
        return f"{self.film} at {self.time}"

class Seats(models.Model):
    row = models.CharField(max_length=1)
    seatno = models.IntegerField(validators=[MaxValueValidator(10)])
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)

class TicketPrice(models.Model):
    child = models.DecimalField(max_digits=5, decimal_places=2)
    student = models.DecimalField(max_digits=5, decimal_places=2)
    adult = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"TicketPrice(child={self.child}, student={self.student}, adult={self.adult})"
    
    
class Booking(models.Model):
    email = models.EmailField()
    showing = models.ForeignKey(Showing, on_delete=models.CASCADE)
    child_tickets = models.PositiveIntegerField(default=0)
    student_tickets = models.PositiveIntegerField(default=0)
    adult_tickets = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.showing.film} - {self.showing.date} - {self.showing.time} - {self.total_price}"

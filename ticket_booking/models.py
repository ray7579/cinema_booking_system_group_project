from django.db import models

# class Screening(models.Model):
#     movie_name = models.CharField(max_length=100)
#     date = models.DateField()
#     time = models.TimeField()
#     total_seats = models.IntegerField(default=50)
#     available_seats = models.IntegerField(default=50)

class Ticket(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=False)
    phone_number = models.CharField(max_length=15)
    ticket_type_choices = (
        ('student', 'Student'),
        ('child', 'Child'),
        ('adult', 'Adult'),
    )
    ticket_type = models.CharField(max_length=7, choices=ticket_type_choices)
    ticket_quantity = models.IntegerField(default=1)
    ticket_price = models.DecimalField(max_digits=5, decimal_places=2, default=11.00)
    total_price = models.DecimalField(max_digits=5, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.ticket_price * self.ticket_quantity
        super().save(*args, **kwargs)

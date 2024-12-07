from django.db import models
import datetime
# Create your models here.

class CreateOrder(models.Model):
    order = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Order ID {self.id} - {'Yes' if self.order else 'No'} in time {self.date}"
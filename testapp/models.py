from django.db import models

# Create your models here.

class CreateOrder(models.Model):
    order = models.BooleanField(default=False)
    def __str__(self):
        return f"Order ID {self.id} - {'Yes' if self.order else 'No'}"
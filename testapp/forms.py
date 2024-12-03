from django import forms
from .models import CreateOrder
class OrderForm(forms.ModelForm):
    class Meta:
        model = CreateOrder
        fields = ['order']
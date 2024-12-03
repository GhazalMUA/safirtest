from django.shortcuts import render, redirect
from .forms import OrderForm

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('order_success')  # Define a success URL or page
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form})

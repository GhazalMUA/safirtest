from django.shortcuts import render, HttpResponse
from .forms import OrderForm
from .tasks import run_selenium_bot
   
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            if order.id:  # Ensure order has been saved and has an id
                run_selenium_bot.delay('testapp_createorder', order.id,'INSERT')  # Call the Celery task asynchronously
            else:
                print("Error: Order ID is missing!")
            return HttpResponse('Order created successfully and task triggered!')
    else:
        form = OrderForm()
    return render(request, 'create_order.html', {'form': form})


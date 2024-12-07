from django.shortcuts import render, HttpResponse
from .forms import OrderForm
from .tasks import run_selenium_bot
   
def create_order(request):
    """
    Handles HTTP POST requests to create a new order and asynchronously triggers 
    the `run_selenium_bot` Celery task after the order is successfully saved.

    Parameters:
    -----------
    - `request`: The HTTP request object.

    Key Features:
    -------------
    1. **Order Creation**:
    - Handles form submission to create a new order using `OrderForm`.
    - Validates the form and saves the order to the database.

    2. **Asynchronous Task Execution**:
    - If the order is successfully saved (i.e., has an ID), triggers the 
        `run_selenium_bot` Celery task with the following parameters:
        - Table name (`'testapp_createorder'`).
        - Order ID (`order.id`).
        - Operation type (`'INSERT'`).

    3. **User Feedback**:
    - Returns a success message after creating the order and triggering the task.
    - Renders the order creation form for GET requests.

    """

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


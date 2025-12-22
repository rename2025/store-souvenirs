from django.shortcuts import render

def order_create(request):
    return render(request, 'orders/create.html')

def order_created(request, order_id):
    return render(request, 'orders/created.html')

def order_history(request):
    return render(request, 'orders/history.html')

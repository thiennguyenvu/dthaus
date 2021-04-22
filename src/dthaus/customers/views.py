from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
from .models import *
from .forms import CustomerCreateForm
brand = 'DONGJIN VIETNAM'

@login_required(login_url='login')
def customers(request):
    title = 'Customers'

    customers = Customer.objects.all()

    context = {
        'brand': brand,
        'title': title,
        'customers': customers,
    }
    
    return render(request, 'customers/customers.html', context)

@login_required(login_url='login')
def customer_create(request):
    title = 'Add New Customer'
    create_form = CustomerCreateForm()

    if request.method == 'POST':
        form = CustomerCreateForm(request.POST)
        if form.is_valid():
            new_customer = form.save()
            return redirect('customers')

    context = {
        'brand': brand,
        'title': title,
        'create_form': create_form,
    }
    return render(request, 'customers/customer-create.html', context)
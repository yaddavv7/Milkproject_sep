from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Customer


def home(request):
    """Home landing page for Milk Distribution Customer Record System."""
    return render(request, 'customers/home.html')


def signup_view(request):
    """User registration view using Django's built-in UserCreationForm."""
    if request.user.is_authenticated:
        return redirect('customer_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'customers/signup.html', {'form': form})


def login_view(request):
    """User login view using authenticate() and login()."""
    if request.user.is_authenticated:
        return redirect('customer_list')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('customer_list')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'customers/login.html')


def logout_view(request):
    """Logout view redirecting to login page."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def customer_list(request):
    """View to list all registered milk distribution customers."""
    customers = Customer.objects.all().order_by('id')
    return render(request, 'customers/customer_list.html', {'customers': customers})


@login_required
def add_customer(request):
    """View to add a new customer record."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        litres_per_day = request.POST.get('litres_per_day', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not name or not address or not litres_per_day or not phone:
            messages.error(request, 'All fields are required. Please fill in all fields.')
            return render(request, 'customers/add_customer.html', {
                'name': name,
                'address': address,
                'litres_per_day': litres_per_day,
                'phone': phone,
            })

        Customer.objects.create(
            name=name,
            address=address,
            litres_per_day=litres_per_day,
            phone=phone
        )
        messages.success(request, 'Customer added successfully!')
        return redirect('customer_list')

    return render(request, 'customers/add_customer.html')


@login_required
def edit_customer(request, id):
    """View to edit an existing customer record."""
    customer = get_object_or_404(Customer, id=id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        litres_per_day = request.POST.get('litres_per_day', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not name or not address or not litres_per_day or not phone:
            messages.error(request, 'All fields are required. Please fill in all fields.')
            return render(request, 'customers/edit_customer.html', {'customer': customer})

        customer.name = name
        customer.address = address
        customer.litres_per_day = litres_per_day
        customer.phone = phone
        customer.save()

        messages.success(request, 'Customer details updated successfully!')
        return redirect('customer_list')

    return render(request, 'customers/edit_customer.html', {'customer': customer})


@login_required
def delete_customer(request, id):
    """View to delete a customer record via POST."""
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
    return redirect('customer_list')

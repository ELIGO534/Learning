from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .models import User
from django.contrib.auth.hashers import make_password
  # If you are using a custom User model

# In your views.py

def login(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']

        # Authenticate user using the custom backend
        user = authenticate(request, phone=phone, password=password)

        if user is not None:
            auth_login(request, user)  # Log the user in
            messages.success(request, 'Login successful!')
            return redirect('home')  # Redirect to homepage or dashboard
        else:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'login.html')

def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "signup.html")

        if User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already exists!")
            return render(request, "signup.html")

        # Hash the password before saving to the database
        hashed_password = make_password(password)
        User.objects.create(name=name, phone=phone, password=hashed_password)

        messages.success(request, "Account created successfully!")
        return redirect("/home/")  # Redirect to login page

    return render(request, "signup.html")

from django.shortcuts import render

def home(request):
    context = {
        'welcome_text': 'Hi, Learner! Welcome to Eligo. Enroute to your future paths through Eligo. Start right now for the introduction video!',
    }
    return render(request, 'home.html', context)

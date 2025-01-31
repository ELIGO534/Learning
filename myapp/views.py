from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .models import Member
from django.contrib.auth.hashers import make_password
from myapp.models import Profile
from myapp.forms import ProfileForm
from django.contrib.auth import get_user_model

User = get_user_model()
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
    return render(request, 'home.html', {'user': request.user})
def level(request):
    user_name = request.user.phone  # Adjust to your need
    return render(request, 'levels.html', {'user_name': user_name})
# views.py
from django.shortcuts import render
from myapp.models import Member

def members(request):
    if request.user.is_authenticated:
        # Get the logged-in user and filter members associated with them
        members_list = Member.objects.filter(user=request.user)
    else:
        members_list = []

    return render(request, 'members.html', {'members': members_list})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile

@login_required


def profile_view(request):
    try:
        # Fetch the profile or raise an exception if it does not exist
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Optionally, create a profile if it doesn't exist
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Ensure 'profile' is defined in your URLs
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form, 'profile': profile})


def withdrawl(request):
    return render(request, 'withdrawl.html')

def chat(request):
    return render(request, 'chat.html')
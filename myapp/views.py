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


def chat(request):
    return render(request, 'chat.html')

def income(request):
    return render(request, 'income.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Withdrawal

# Define allowed phone numbers
ALLOWED_NUMBERS = {"7893355365"}  # Update this list as needed

@login_required
def transactions(request):
    profile = request.user.profile  # Assuming a profile model linked to User
    
    # Check if the user's phone number is in the allowed list
    if profile.phone_number not in ALLOWED_NUMBERS:
        return redirect("/withdrawal/")  # Redirect unauthorized users
    
    # Fetch all withdrawal transactions for the logged-in user
    transactions = Withdrawal.objects.filter(user=request.user).order_by("-id")  
    
    return render(request, "transactions.html", {"transactions": transactions})


from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Withdrawal
from .forms import WithdrawalForm

@login_required
def withdrawl(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None

    if request.method == "POST":
        form = WithdrawalForm(request.POST)  # ✅ Corrected: Use WithdrawalForm, not Withdrawal
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.user = request.user

            withdrawal_amount = Decimal(form.cleaned_data["amount"])

            if profile and withdrawal_amount <= profile.balance:
                profile.balance -= withdrawal_amount
                profile.save()

                withdrawal.save()
                
                messages.success(request, "Withdrawal successful!")
                return redirect("withdrawl")  
            else:
                messages.error(request, "❌ Please check your available balance.")  # ✅ Error Message

    else:
        form = WithdrawalForm()

    return render(request, "withdrawl.html", {"form": form, "balance": profile.balance if profile else Decimal("0.00")})

def withdrawal_students(request):
    return render(request, "withdrawal_s.html")

def join_members(request):
    return render(request, "join.html")
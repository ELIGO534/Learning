from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .models import Member
from django.contrib.auth.hashers import make_password
from myapp.models import Profile
from myapp.forms import ProfileForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

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
            return redirect('profile')  # Redirect to homepage or dashboard
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


def home(request):
    return render(request, 'home.html', {'user': request.user})
from django.shortcuts import render, redirect
from .models import Profile  # Ensure you have this model

# Manually define phone numbers that should have access to Stage 1
SELECTED_USERS_FOR_STAGE_1 = ['7989709833', '9876543210']  # Add phone numbers here

def level(request):
    user_name = request.user.phone  # Assuming 'phone' is the field you're using
    user_has_access_to_stage_1 = user_name in SELECTED_USERS_FOR_STAGE_1
    user_profile = Profile.objects.get(user=request.user)  # Assuming user_profile is linked to user
    message = ""
    
    # Checking if the user is at Stage 1
    if user_has_access_to_stage_1:
        message = "Congratulations! Now you are an Initiator and have referred 20 people. Your referred amount is already updated in your profile."
    
    if request.method == "POST" and user_has_access_to_stage_1:
        # Adding 500 points to the user's balance when the button is clicked
        user_profile.balance += 500  # Add the 500 points to the current balance
        user_profile.save()  # Save the updated profile
        message = f"{message} Your balance has been updated with 500 points."

    return render(request, 'levels.html', {
        'user_name': user_name,
        'stage_message': message,
        'balance': user_profile.balance,  # Passing the balance to the template
    })



# views.py
from django.shortcuts import render
from myapp.models import Member

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Member, Profile  # Import your profile model

@login_required
def members(request):
    if request.user.is_authenticated:
        # Get the logged-in user's members
        members_list = Member.objects.filter(user=request.user)
        
        # Get or create the user's profile
        profile = Profile.objects.get_or_create(user=request.user)
    else:
        members_list = []
        profile = None  # or you could create an anonymous profile with 0 earnings

    return render(request, 'members.html', {
        'members': members_list,
        'profile': profile  # Now passing the profile to template
    })

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




from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Withdrawal
from .forms import WithdrawalForm

@login_required
def withdrawl(request):
    """Handles the withdrawal request and updates the user's balance."""
    allowed_phone_numbers = ['0987654321','7989709833','9652871191','7893355365','9666156431','7670812001','7093028071']  # Add allowed phone numbers here

    # Ensure the user has a profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Check if the user's phone number is in the allowed list
    is_authorized = request.user.phone in allowed_phone_numbers

    if request.method == "POST" and is_authorized:
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.user = request.user
            withdrawal_amount = Decimal(form.cleaned_data["amount"])

            # Check for a valid withdrawal amount
            if withdrawal_amount <= 0:
                messages.error(request, "❌ Invalid withdrawal amount. Please enter a positive amount.")
            elif profile.balance >= withdrawal_amount:
                # Deduct amount and save profile
                profile.balance -= withdrawal_amount
                profile.save()

                # Set withdrawal status to pending and save
                withdrawal.payment_status = "Pending"
                withdrawal.save()

                messages.success(request, "✅ Withdrawal request submitted successfully!")
                return redirect("transactions")  # Redirect to transactions page
            else:
                messages.error(request, "❌ Insufficient balance.")
    else:
        form = WithdrawalForm()

    return render(request, "withdrawl.html", {"form": form, "balance": profile.balance, "is_authorized": is_authorized})



import uuid

@login_required
def transactions(request):
    """Displays the user's withdrawal transaction history."""
    
    # Get all withdrawals for the logged-in user
    withdrawals = Withdrawal.objects.filter(user=request.user)

    # Add a unique transaction ID to each withdrawal
    for withdrawal in withdrawals:
        withdrawal.transaction_id = uuid.uuid4().hex[:8]  # Or any format you'd like

    return render(request, "transactions.html", {"withdrawals": withdrawals})



def withdrawal_students(request):
    return render(request, "withdrawal_s.html")

def join_members(request):
    return render(request, "join.html")

def my_courses(request):
    context = {
    'data_analysis_numbers': [
        "9063047813", "7989219165", "9346181489", "7396252699", "6305969920", "7386323303",
        "6301377530", "7382579283", "8309621284", "9618944742", "6305376046", "9063182706",
        "7847887022", "6301740212", "9959134659", "9100792452", "9704261549", "9398940353",
        "7207794091", "7989709833"
    ],

    'web_dev_numbers': [
        "9963242195", "9347844479", "7842351513", "9381700503", "6281371577", "7386376764",
        "7207674531", "8639454686", "8341633481", "9347709402", "9010134688", "9985317855",
        "9100390114", "9014574670", "8125274748", "7013627174", "9346053083", "9390427208",
        "6281808939", "8500166525", "8790413984", "9381987419", "6301382198", "8247836086",
        "6302451271", "6281850287", "8977709225", "8125883892", "6302186722", "8919272658",
        "8309138848", "6301242839", "7075303564", "9989026209", "6301520199"
    ],

    'ml_numbers': [
        "8328480287", "7337050706", "8712837063",
        "9603689566", "8712385254", "9908191735"
    ],
}

    return render(request, 'my_courses.html', context)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Profile

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def collect_stage1_reward(request):
    # Get the user's profile
    user_profile = Profile.objects.get(user=request.user)

    # If the request is a POST (the user clicked the "Collect ₹500" button)
    if request.method == "POST":
        # Check if the user hasn't collected the reward yet
        if not user_profile.has_collected_stage1:
            user_profile.balance += 500  # Add ₹500 to the user's balance
            user_profile.has_collected_stage1 = True  # Mark as collected
            user_profile.save()

            # Return a response with the updated balance
            return JsonResponse({
                "new_balance": user_profile.balance,
                "success": True
            })

        # If the user already collected the reward, don't do anything
        return JsonResponse({
            "error": "You have already collected the ₹500!",
            "success": False
        })

    # If the request is a GET (rendering the page)
    has_collected_stage1 = user_profile.has_collected_stage1
    current_balance = user_profile.balance

    return render(request, "levels.html", {
        "has_collected_stage1": has_collected_stage1,
        "current_balance": current_balance,
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Profile
import json

@csrf_exempt
@login_required
def update_balance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount', 0)

            # Get the user's profile
            profile = Profile.objects.get(user=request.user)

            # Update the balance
            profile.balance += amount
            profile.save()

            return JsonResponse({'success': True, 'new_balance': profile.balance})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def help(request):
    return render(request,'needhelp.html')
def upload(request):
    return render(request,'upload.html')
def uploadsuccess(request):
    return render(request,'uploadsuccess.html')
def about(request):
    return render(request,'about.html')
def courses(request):
    return render(request,'courses.html')
@login_required
def my_learning(request):
    return render(request, 'my_learning.html')
def contact(request):
    return render(request, "contact.html")
def payment_success(request):
    return render(request, 'payment_success.html')
def privacypolicy(request):
    return render(request, 'privacypolicy.html')
def sponsors(request):
    return render(request,"sponsors.html")
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.shortcuts import render
from .models import SponsorshipSurvey

def survey_page(request):
    return render(request, "learnmore.html")  # Ensure the correct template is rendered

@csrf_exempt  # If you're using Fetch API without CSRF token, keep this
def submit_survey(request):
    if request.method == "POST":
        contact = request.POST.get("contact")
        email = request.POST.get("email")

        # Check if the contact number already exists before saving
        if SponsorshipSurvey.objects.filter(contact=contact).exists():
            return JsonResponse(
                {"success": False, "message": "The form has already been pre-filled with this number!"},
                status=400
            )

        # Check if the email already exists before saving
        if SponsorshipSurvey.objects.filter(email=email).exists():
            return JsonResponse(
                {"success": False, "message": "Email is already taken!"},
                status=400
            )

        try:
            # Extract form data
            full_name = request.POST.get("fullName")
            college = request.POST.get("college")
            year = request.POST.get("year")
            source = request.POST.get("source")
            interest = request.POST.getlist("interest")  # Handle multiple interests
            internship = request.POST.get("internship")
            updates = request.POST.get("updates")

            # Ensure required fields are not empty
            if not full_name or not email or not college or not contact:
                return JsonResponse(
                    {"success": False, "message": "Missing required fields!"},
                    status=400
                )

            # Save data
            SponsorshipSurvey.objects.create(
                full_name=full_name,
                email=email,
                college=college,
                year=year,
                source=source,
                interest=",".join(interest),  # Convert list to comma-separated string
                internship=internship,
                updates=updates,
                contact=contact
            )

            return JsonResponse(
                {"success": True, "message": "Form submitted successfully!"},
                status=200
            )

        except IntegrityError:  # Handle unique constraint violation
            return JsonResponse(
                {"success": False, "message": "The form has already been pre-filled with this number or email!"},
                status=400
            )

        except Exception as e:  # Handle other exceptions
            return JsonResponse(
                {"success": False, "message": f"Error: {str(e)}"},
                status=400
            )

    # Handle invalid request method
    return JsonResponse(
        {"success": False, "message": "Invalid request method!"},
        status=400
    )

def employee_page(request):
    return render(request, 'index.html')


# In your view
@login_required
def my_learning(request):
    context = {
    'data_analysis_numbers': [
        "9063047813", "7989219165", "9346181489", "7396252699", "6305969920", "7386323303",
        "6301377530", "7382579283", "8309621284", "9618944742", "6305376046", "9063182706",
        "7847887022", "6301740212", "9959134659", "9100792452", "9704261549", "9398940353",
        "7207794091"
    ],

    'web_dev_numbers': [
        "9963242195", "9347844479", "7842351513", "9381700503", "6281371577", "7386376764",
        "7207674531", "8639454686", "8341633481", "9347709402", "9010134688", "9985317855",
        "9100390114", "9014574670", "8125274748", "7013627174", "9346053083", "9390427208",
        "6281808939", "8500166525", "8790413984", "9381987419", "6301382198", "8247836086",
        "6302451271", "6281850287", "8977709225", "8125883892", "6302186722", "8919272658",
        "8309138848", "6301242839", "7075303564", "9989026209", "7989709833", "6301520199"
    ],

    'ml_numbers': [
        "8328480287", "7337050706", "8712837063",
        "9603689566", "8712385254", "9908191735"
    ],
}

    return render(request, 'my_learning.html', context)

def internships(request):
    return render(request , 'internships.html')

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to home page after logout

def courseoffer(request):
    return render(request, 'courseoffer.html')
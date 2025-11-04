from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import Member, Profile, Withdrawal, SponsorshipSurvey, UserActivity
from django.contrib.auth.hashers import make_password
from .forms import ProfileForm, WithdrawalForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import uuid
from decimal import Decimal
import json
from datetime import datetime, timedelta
from django.db.models import Count

User = get_user_model()

# Helper function to track user activity
def track_activity(user, action, details=None):
    UserActivity.objects.create(
        user=user,
        action=action,
        details=details or {}
    )

def login(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        user = authenticate(request, phone=phone, password=password)

        if user is not None:
            auth_login(request, user)
            
            # Track login activity
            track_activity(user, 'login', {
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            })
            
            # Update last login time and login count
            profile, created = Profile.objects.get_or_create(user=user)
            profile.login_count += 1
            profile.last_login = datetime.now()
            profile.save()
            
            messages.success(request, 'Login successful!')
            return redirect('profile')
        else:
            # Track failed login attempt
            if User.objects.filter(phone=phone).exists():
                user = User.objects.get(phone=phone)
                track_activity(user, 'failed_login', {
                    'attempted_with': phone,
                    'ip_address': request.META.get('REMOTE_ADDR')
                })
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

        hashed_password = make_password(password)
        user = User.objects.create(name=name, phone=phone, password=hashed_password)
        
        # Track signup activity
        track_activity(user, 'signup', {
            'ip_address': request.META.get('REMOTE_ADDR'),
            'signup_method': 'web'
        })
        
        messages.success(request, "Account created successfully!")
        return redirect("/home/")

    return render(request, "signup.html")

def home(request):
    if request.user.is_authenticated:
        # Track homepage visit
        track_activity(request.user, 'homepage_visit')
    return render(request, 'home.html', {'user': request.user})

# Manually define phone numbers that should have access to Stage 1
SELECTED_USERS_FOR_STAGE_1 = ['7989709833', '9876543210']

@login_required
def level(request):
    user_name = request.user.phone
    user_has_access_to_stage_1 = user_name in SELECTED_USERS_FOR_STAGE_1
    user_profile = Profile.objects.get(user=request.user)
    message = ""
    
    # Track level page visit
    track_activity(request.user, 'level_page_visit', {
        'has_stage1_access': user_has_access_to_stage_1,
        'current_balance': float(user_profile.balance)
    })
    
    if user_has_access_to_stage_1:
        message = "Congratulations! Now you are an Initiator and have referred 20 people. Your referred amount is already updated in your profile."
    
    if request.method == "POST" and user_has_access_to_stage_1:
        user_profile.balance += 500
        user_profile.save()
        
        # Track reward collection
        track_activity(request.user, 'stage1_reward_collected', {
            'amount_added': 500,
            'new_balance': float(user_profile.balance)
        })
        
        message = f"{message} Your balance has been updated with 500 points."

    return render(request, 'levels.html', {
        'user_name': user_name,
        'stage_message': message,
        'balance': user_profile.balance,
    })

@login_required
def members(request):
    members_list = Member.objects.filter(user=request.user)
    profile = Profile.objects.get_or_create(user=request.user)
    
    # Track members page visit
    track_activity(request.user, 'members_page_visit', {
        'member_count': members_list.count()
    })
    
    return render(request, 'members.html', {
        'members': members_list,
        'profile': profile[0]
    })

@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            
            # Track profile update
            track_activity(request.user, 'profile_updated', {
                'fields_updated': list(form.cleaned_data.keys())
            })
            
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
        
    # Track profile page visit
    track_activity(request.user, 'profile_page_visit')

    return render(request, 'profile.html', {'form': form, 'profile': profile})

def chat(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'chat_page_visit')
    return render(request, 'chat.html')

def income(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'income_page_visit')
    return render(request, 'income.html')

@login_required
def withdrawl(request):
    allowed_phone_numbers = ['0987654321','7989709833','9652871191','7893355365','9666156431','7670812001','7093028071','8688162274','6281508930', '7386362971', '8008027719', '9052778174', '7989860150', '9398130940', '6309541099', '7893225446', '7989406927', '9573543556', '7396244347', '9391223486', '6302031614', '9059254524', '9705682444', '7013328126', '9346384707', '9381044755', '7386903365', '8184929428', '9110323949', '8985067550', '6309694696', '8688162274', '7386677677', '7483160050', '9392739861', '8341445547', '9182752749', '8977838924', '9398758167', '7337300747','8977838924','8341445547','9182752749','7660945966','9398758167','7337300747','7989438913','7981397626','9652470696','9347338524']
    profile, created = Profile.objects.get_or_create(user=request.user)
    is_authorized = request.user.phone in allowed_phone_numbers

    if request.method == "POST" and is_authorized:
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.user = request.user
            withdrawal_amount = Decimal(form.cleaned_data["amount"])

            if withdrawal_amount <= 0:
                messages.error(request, "❌ Invalid withdrawal amount. Please enter a positive amount.")
            elif profile.balance >= withdrawal_amount:
                profile.balance -= withdrawal_amount
                profile.save()
                withdrawal.payment_status = "Pending"
                withdrawal.save()
                
                # Track withdrawal request
                track_activity(request.user, 'withdrawal_requested', {
                    'amount': float(withdrawal_amount),
                    'new_balance': float(profile.balance),
                    'payment_method': withdrawal.payment_method
                })
                
                messages.success(request, "✅ Withdrawal request submitted successfully!")
                return redirect("transactions")
            else:
                messages.error(request, "❌ Insufficient balance.")
    else:
        form = WithdrawalForm()
        
    # Track withdrawal page visit
    track_activity(request.user, 'withdrawal_page_visit', {
        'current_balance': float(profile.balance),
        'is_authorized': is_authorized
    })

    return render(request, "withdrawl.html", {"form": form, "balance": profile.balance, "is_authorized": is_authorized})

@login_required
def transactions(request):
    withdrawals = Withdrawal.objects.filter(user=request.user)
    
    # Track transactions page visit
    track_activity(request.user, 'transactions_page_visit', {
        'withdrawal_count': withdrawals.count()
    })
    
    return render(request, "transactions.html", {"withdrawals": withdrawals})

def withdrawal_students(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'withdrawal_students_page_visit')
    return render(request, "withdrawal_s.html")

def join_members(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'join_members_page_visit')
    return render(request, "join.html")


@login_required
def collect_stage1_reward(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if not user_profile.has_collected_stage1:
            user_profile.balance += 500
            user_profile.has_collected_stage1 = True
            user_profile.save()

            # Track reward collection
            track_activity(request.user, 'stage1_reward_collected', {
                'amount_added': 500,
                'new_balance': float(user_profile.balance)
            })

            return JsonResponse({
                "new_balance": user_profile.balance,
                "success": True
            })

        return JsonResponse({
            "error": "You have already collected the ₹500!",
            "success": False
        })

    has_collected_stage1 = user_profile.has_collected_stage1
    current_balance = user_profile.balance

    return render(request, "levels.html", {
        "has_collected_stage1": has_collected_stage1,
        "current_balance": current_balance,
    })

@csrf_exempt
@login_required
def update_balance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount', 0)

            profile = Profile.objects.get(user=request.user)
            profile.balance += amount
            profile.save()
            
            # Track balance update
            track_activity(request.user, 'balance_updated', {
                'amount': amount,
                'new_balance': float(profile.balance),
                'source': 'manual_update'
            })

            return JsonResponse({'success': True, 'new_balance': profile.balance})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def help(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'help_page_visit')
    return render(request,'needhelp.html')

def upload(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'upload_page_visit')
    return render(request,'upload.html')

def uploadsuccess(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'upload_success_page_visit')
    return render(request,'uploadsuccess.html')

def about(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'about_page_visit')
    return render(request,'about.html')

def courses(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'courses_page_visit')
    return render(request,'courses.html')

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
        "8309138848", "6301242839", "7075303564", "9989026209", "7989709833",
        "7013085054", "9346800335", "7996154586", "6301520199" , "7671835583", "6301520199"
    ,   "9705682444", "7013328126", "9346384707", "9996660001",
        "7989709836", "9398130940", "6309541099", "7893225446",
        "8688498942", "9398130940", "6301825374", "7386794429", "6303143649", "9951426289",
        "6309541099", "8977768418", "8978835762", "9059893869", "7780561820", "9390007420",
        "9502381975", "7396244347", "9391223486", "6302031614","7660984583", "7660984586","9999999999"
        ],

    'ml_numbers': [
        "8328480287", "7337050706", "8712837063",
        "9603689566", "8712385254", "9908191735","9603689566"
    ],
    
    'rohitteam' : [
        "8712837063" , "8712385254", "9908191735", "9603689566"
    ],
    'autocad' : [
        "9866343114","6281508930","8008027719","9052778174","7989860150","7989406927"
    ],
    'java' : [
        "8688162274","7386677677","7483160050","9392739861","6309694696","7483160050","8184929428","9110323949","9381044755", "7386903365", "8985067550"
    ],
    'javafullstack' : [
        "8688162274","7386677677","7483160050","9392739861","6309694696","7483160050","8184929428","9110323949","9381044755", "7386903365", "8985067550"
    ]
    }
    
    track_activity(request.user, 'my_learning_page_visit')
    
    return render(request, 'my_learning.html', context)

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
        "8309138848", "6301242839", "7075303564", "9989026209", "7013085054", "6301520199",
        "9346800335", "7996154586", "7671835583", "9705682444", "7013328126", "9346384707",
        "9398130940", "6309541099", "7893225446", "9996660001",
        "8688498942", "9398130940", "6301825374", "7386794429", "6303143649", "9951426289",
        "6309541099", "8977768418", "8978835762", "9059893869", "7780561820", "9390007420",
        "9502381975", "7396244347", "9391223486", "6302031614", "7660984586", "9999999999"
    ],

    'ml_numbers': [
        "8328480287", "7337050706", "8712837063",
        "9603689566", "8712385254", "9908191735","9603689566"
    ],

    'autocad' : [
        "9866343114","6281508930","8008027719","9052778174","7989860150"
    ],
    'javafullstack' : [
        "8688162274","7386677677","7483160050","9392739861","6309694696","7483160050","8184929428","9110323949","9381044755", "7386903365", "8985067550"
    ],
    'java' : [
        "8688162274","7386677677","7483160050","9392739861","6309694696","7483160050","8184929428","9110323949","9381044755", "7386903365", "8985067550"
    ],
    
    }
    
    if request.user.is_authenticated:
        track_activity(request.user, 'my_courses_page_visit')

    return render(request, 'my_courses.html', context)


def internships(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'internships_page_visit')
    return render(request , 'internships.html')

@login_required
def logout_view(request):
    # Track logout activity
    track_activity(request.user, 'logout', {
        'session_duration': (datetime.now() - request.user.last_login).total_seconds() if request.user.last_login else 0
    })
    
    logout(request)
    return redirect('home')

def courseoffer(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'courseoffer_page_visit')
    return render(request, 'courseoffer.html')

def assignments(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'assignments_page_visit')
    return render(request, 'assignments.html')

def contact(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'contact_page_visit')
    return render(request, "contact.html")

def payment_success(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'payment_success_page_visit')
    return render(request, 'payment_success.html')

def privacypolicy(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'privacypolicy_page_visit')
    return render(request, 'privacypolicy.html')

def sponsors(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'sponsors_page_visit')
    return render(request,"sponsors.html")

def survey_page(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'survey_page_visit')
    return render(request, "learnmore.html")

def careers(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'carrer_page_visit')
    return render(request, "careers.html")

@csrf_exempt
def submit_survey(request):
    if request.method == "POST":
        contact = request.POST.get("contact")
        email = request.POST.get("email")

        if SponsorshipSurvey.objects.filter(contact=contact).exists():
            return JsonResponse(
                {"success": False, "message": "The form has already been pre-filled with this number!"},
                status=400
            )

        if SponsorshipSurvey.objects.filter(email=email).exists():
            return JsonResponse(
                {"success": False, "message": "Email is already taken!"},
                status=400
            )

        try:
            full_name = request.POST.get("fullName")
            college = request.POST.get("college")
            year = request.POST.get("year")
            source = request.POST.get("source")
            interest = request.POST.getlist("interest")
            internship = request.POST.get("internship")
            updates = request.POST.get("updates")

            if not full_name or not email or not college or not contact:
                return JsonResponse(
                    {"success": False, "message": "Missing required fields!"},
                    status=400
                )

            SponsorshipSurvey.objects.create(
                full_name=full_name,
                email=email,
                college=college,
                year=year,
                source=source,
                interest=",".join(interest),
                internship=internship,
                updates=updates,
                contact=contact
            )
            
            # Track survey submission
            if request.user.is_authenticated:
                track_activity(request.user, 'survey_submitted', {
                    'survey_type': 'sponsorship'
                })

            return JsonResponse(
                {"success": True, "message": "Form submitted successfully!"},
                status=200
            )

        except IntegrityError:
            return JsonResponse(
                {"success": False, "message": "The form has already been pre-filled with this number or email!"},
                status=400
            )

        except Exception as e:
            return JsonResponse(
                {"success": False, "message": f"Error: {str(e)}"},
                status=400
            )

    return JsonResponse(
        {"success": False, "message": "Invalid request method!"},
        status=400
    )

def employee_page(request):
    if request.user.is_authenticated:
        track_activity(request.user, 'employee_page_visit')
    return render(request, 'index.html')

@login_required
def activity_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    activities = UserActivity.objects.all().order_by('-timestamp')[:100]
    user_stats = {}
    
    users = User.objects.filter(useractivity__isnull=False).distinct()
    
    for user in users:
        user_activities = UserActivity.objects.filter(user=user)
        user_stats[user.phone] = {
            'total_activities': user_activities.count(),
            'last_activity': user_activities.first().timestamp if user_activities.exists() else None,
            'login_count': user_activities.filter(action='login').count(),
            'common_actions': dict(user_activities.values_list('action').annotate(count=Count('action')).order_by('-count')[:5])
        }
    
    # Track admin dashboard access
    track_activity(request.user, 'admin_dashboard_accessed')
    
    return render(request, 'activity_dashboard.html', {
        'activities': activities,
        'user_stats': user_stats,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(useractivity__timestamp__gte=datetime.now()-timedelta(days=7)).distinct().count(),
        'recent_signups': User.objects.filter(date_joined__gte=datetime.now()-timedelta(days=7)).count()
    })


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.utils import timezone
from .models import UserActivity, CustomUser, Profile
from django.db.models import Count, Q, OuterRef, Subquery
from datetime import timedelta

@user_passes_test(lambda u: u.is_superuser)
def user_activity_dashboard(request):
    # Active users (logged in last 15 minutes)
        active_users = CustomUser.objects.filter(
            last_login__gte=timezone.now()-timedelta(minutes=15))
    
    # User login stats
        user_stats = CustomUser.objects.annotate(
        activity_count=Count('useractivity'),
        last_activity=Subquery(
            UserActivity.objects.filter(
                user=OuterRef('pk')
            ).order_by('-timestamp').values('timestamp')[:1]
        )
    ).select_related('profile')
    
    # Inactive users (no login in 30 days)
        inactive_users = CustomUser.objects.filter(
        last_login__lte=timezone.now()-timedelta(days=30))
    
    # Activity metrics
        total_logins = UserActivity.objects.filter(action='login').count()
        recent_activities = UserActivity.objects.all().order_by('-timestamp')[:20]
    
        context = {
        'active_users': active_users,
        'user_stats': user_stats,
        'inactive_users': inactive_users,
        'total_logins': total_logins,
        'recent_activities': recent_activities,
        'now': timezone.now()
    }
        return render(request, 'dashboard.html', context)

# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .models import AssignmentSubmission
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET", "POST"])
def assignment_view(request):
    if request.method == 'POST':
        return handle_file_upload(request)
    return handle_get_request(request)

def handle_file_upload(request):
    try:
        # Validate file exists in request
        if 'documentation' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file was uploaded'
            }, status=400)

        file = request.FILES['documentation']
        
        # Validate file size (50MB max)
        if file.size > 50 * 1024 * 1024:
            return JsonResponse({
                'success': False, 
                'error': 'File size exceeds 50MB limit'
            }, status=400)

        # Save file and create record
        submission = AssignmentSubmission.objects.create(
            user=request.user,
            documentation=file,
            status='submitted'
        )

        return JsonResponse({
            'success': True,
            'message': 'File uploaded successfully',
            'file_url': submission.documentation.url,
            'submission_id': submission.id
        })

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An internal server error occurred'
        }, status=500)

def handle_get_request(request):
    try:
        submissions = AssignmentSubmission.objects.filter(
            user=request.user
        ).order_by('-submitted_at')
        
        return render(request, 'assignments.html', {
            'submissions': submissions
        })
    except Exception as e:
        logger.error(f"Page load failed: {str(e)}", exc_info=True)
        return render(request, 'error.html', {
            'error': 'Failed to load assignments'
        }, status=500)

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views

urlpatterns = [
    path('',views.login, name='login'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    path('levels/', views.level, name='levels'),
    path('members/', views.members, name='members'),
    path('withdrawl/', views.withdrawl, name='withdrawl'),
    path('chat/', views.chat, name='chat'),
    path('profile/', views.profile_view, name='profile'),
    path('income/', views.income, name='income'),
    path('my_courses/', views.my_courses, name='my_courses'),
    path('withdrawal/', views.withdrawal_students, name='withdrawal'),
    path('join_members/', views.join_members, name='join'),
    path('update-balance/', views.update_balance, name='update_balance'),
    path('transaction/', views.transactions, name='transactions'),
    path("collect-stage1-reward/", views.collect_stage1_reward, name="collect_stage1_reward"), # Add this
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Home page view

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
    path('transactions/', views.transactions, name='transactions'),
    path('withdrawal/', views.withdrawal_students, name='withdrawal'),
    path('join_members/', views.join_members, name='join'),
    path('transaction/', views.transactions, name='transactions'), # Add this
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Home page view

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views

urlpatterns = [
    path('',views.home, name='home'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('careers/', views.careers, name='careers'),
    path('my_learning/', views.my_learning, name='dashboard'),
    path('internships/', views.internships, name='internships'),
    path('levels/', views.level, name='levels'),
    path('referrals/', views.members, name='members'),
    path('withdrawl/', views.withdrawl, name='withdrawl'),
    path('chatwithus/', views.chat, name='chat'),
    path('profile/', views.profile_view, name='profile'),
    path('contact/', views.contact, name='contact'),
    path('survey/', views.survey_page, name='survey_page'),
    path('survey/submit/', views.submit_survey, name='submit_survey'),
    path('income/', views.income, name='income'),
    path('my_courses/', views.my_courses, name='my_courses'),
    path('assignments/', views.assignments, name='assignments'),
    path('sponsorship/', views.sponsors, name='sponsors'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('privacypolicy/', views.privacypolicy, name='privacypolicy'),
    path('join_members/', views.join_members, name='join'),
    path('update-balance/', views.update_balance, name='update_balance'),
    path('transaction/', views.transactions, name='transactions'),
    path('needhelp/', views.help, name='needhelp'),
    path('upload/', views.upload, name='upload'),
    path('courseoffer/', views.courseoffer, name='courseoffer'),
    path('uploadsuccess/', views.uploadsuccess, name='uploadsuccess'),
    path('logout/', views.logout_view, name='logout'),
    path("collect-stage1-reward/", views.collect_stage1_reward, name="collect_stage1_reward"), # Add this
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Home page view

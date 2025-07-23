from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from django.db.models import JSONField

# Custom Manager for User model
class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("The Phone number must be set")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone, password, **extra_fields)

# Custom User model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.phone})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

# User Activity Tracking Model
class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    details = JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.phone} - {self.action} at {self.timestamp}"

# Member model related to the User model
class Member(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="members")
    referral = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Pending', 'Pending')])
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.referral} ({self.get_payment_status_display()})"

# Profile model related to the User model
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    withdrawal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    earnings = models.IntegerField(default=0)
    login_count = models.IntegerField(default=0)
    has_collected_stage1 = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.phone} - ₹{self.balance}"

    def get_balance(self):
        return self.balance

    class Meta:
        verbose_name_plural = "Profiles"

class Withdrawal(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Paytm', 'Paytm'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
        ("Rejected", "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='UPI')
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending"
    )
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:  # Ensure it's an update (not a new record)
            old_instance = Withdrawal.objects.get(pk=self.pk)
            if old_instance.payment_status != "Rejected" and self.payment_status == "Rejected":
                # Refund the amount to the user's profile balance
                if hasattr(self.user, 'profile'):
                    self.user.profile.balance += self.amount
                    self.user.profile.save()
            elif old_instance.payment_status == "Pending" and self.payment_status == "Paid":
                self.processed_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.phone} - ₹{self.amount} ({self.get_payment_status_display()})"

    class Meta:
        ordering = ['-created_at']

class SponsorshipSurvey(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    college = models.CharField(max_length=200)
    year = models.CharField(max_length=20)
    source = models.CharField(max_length=50)
    interest = models.TextField()  # Store multiple interests as a comma-separated string
    internship = models.CharField(max_length=10, null=True, blank=True)
    updates = models.CharField(max_length=3)
    contact = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_contacted = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.college})"

    class Meta:
        verbose_name_plural = "Sponsorship Surveys"
        ordering = ['-created_at']

from django.db import models
from django.conf import settings
from django.utils import timezone

class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),  # Added status
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    documentation = models.FileField(upload_to='assignments/%Y/%m/%d/')
    submitted_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    feedback = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Assignment Submission'
        verbose_name_plural = 'Assignment Submissions'
    
    def __str__(self):
        return f"{self.user.username} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

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

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

# Member model related to the User model
class Member(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="members")
    referral = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Pending', 'Pending')])
    temp_field = models.CharField(max_length=100, default="test") 

    def __str__(self):
        return self.referral

# Profile model related to the User model
from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
  
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    withdrawal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.user.phone} - {self.phone_number if self.phone_number else 'No Phone'}"
    
    def get_balance(self):
        return self.balance  # This will return the balance for the user

    
from django.db import models
from django.conf import settings

class Withdrawal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    PAYMENT_STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
        ("Rejected", "Rejected"),
    ]

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:  # Ensure it's an update (not a new record)
            old_instance = Withdrawal.objects.get(pk=self.pk)
            if old_instance.payment_status != "Rejected" and self.payment_status == "Rejected":
                # Refund the amount to the user's profile balance
                if self.user and hasattr(self.user, "profile"):
                    self.user.profile.balance += self.amount
                    self.user.profile.save()

        super().save(*args, **kwargs)

    def __str__(self):
        if self.user and hasattr(self.user, "phone"):
            return f"{self.user.phone} - ₹{self.amount} - {self.payment_status}"
        else:
            return f"Unknown User - ₹{self.amount} - {self.payment_status}"

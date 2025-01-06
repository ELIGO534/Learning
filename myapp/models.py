from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        """
        Creates and returns a regular user with phone and password.
        """
        if not phone:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)  # Automatically hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """
        Creates and returns a superuser with phone and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone, password, **extra_fields)

class User(AbstractBaseUser):
    name = models.CharField(max_length=100)  # New field for name
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)  # Store hashed password
    is_staff = models.BooleanField(default=False)  # To give access to admin
    is_active = models.BooleanField(default=True)  # To check if the user is active

    # This is how Django knows what field to use for authentication
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']  # Fields that are required when creating a user via the admin panel

    objects = UserManager()  # Attach the custom manager

    def __str__(self):
        return self.phone

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt')):
            self.password = make_password(self.password)  # Hash password before saving
        super(User, self).save(*args, **kwargs)

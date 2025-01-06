# In your app directory, create a file named backends.py
from django.contrib.auth.backends import BaseBackend
from .models import User

class PhoneBackend(BaseBackend):
    def authenticate(self, request, phone=None, password=None):
        try:
            user = User.objects.get(phone=phone)  # Get user by phone number
            if user.check_password(password):  # Check password
                return user
        except User.DoesNotExist:
            return None

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'phone_number']

from django import forms
from .models import Withdrawal

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ["name", "account_number", "ifsc_code", "amount"]

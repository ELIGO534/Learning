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

from .models import SponsorshipSurvey

class SponsorshipSurveyForm(forms.ModelForm):
    interest = forms.MultipleChoiceField(
        choices=[
            ("IT", "IT & Software Development"),
            ("AI", "AI & Machine Learning"),
            ("Marketing", "Marketing & Business"),
            ("Design", "UI/UX Design"),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = SponsorshipSurvey
        fields = '__all__'

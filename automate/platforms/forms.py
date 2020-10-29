from django import forms
from platforms.models import BroadworksPlatform


class BroadworksPlatformForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = BroadworksPlatform
        exclude = []
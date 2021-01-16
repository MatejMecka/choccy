from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import CustomUser, StellarAccount, PublicProfile
from .choices import ASSET_CHOICES
class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username',)

class ChangeUserInfo(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')


class ChangeStellarPublicKey(forms.ModelForm):

    class Meta:
        model = StellarAccount
        fields = ('public_key',)

class StellarPrivateKeyForm(forms.Form):
    private_key = forms.CharField(label='Stellar Private Key', max_length=100)

class EditProfile(forms.ModelForm):

    class Meta:
        model = PublicProfile
        fields = ('short_description', 'description', 'image_url', 'twitter_profile')

class PaymentForm(forms.Form):
    asset = forms.ChoiceField(choices = ASSET_CHOICES, required=True)
    asset_name = forms.CharField(label="Asset", required=False)
    asset_issuer = forms.CharField(label="Issuer", required=False)
    amount = forms.IntegerField()
    private_key = forms.CharField(label='Stellar Private Key', max_length=100)

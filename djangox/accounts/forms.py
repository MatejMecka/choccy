from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import CustomUser

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
        fields = ('username','first_name', 'last_name', 'email')
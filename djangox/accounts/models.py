from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.db import models

class CustomUser(AbstractUser):
    first_name = models.CharField(blank=False, null=False, max_length=150)
    last_name = models.CharField(blank=False, null=False, max_length=150)

    def __str__(self):
        return self.email

class StellarAccount(models.Model):
    """
    Model representing the relationship between a user and a Stellar account
    """
    accountId =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    public_key = models.CharField(max_length=300)

    def __str__(self):
        return self.accountId.username
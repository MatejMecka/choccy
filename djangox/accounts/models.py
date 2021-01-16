from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.db import models

class CustomUser(AbstractUser):
    pass

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
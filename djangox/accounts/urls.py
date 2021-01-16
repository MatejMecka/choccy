from django.urls import path

from .views import edit_account_info

urlpatterns = [
    path('edit-account/', edit_account_info, name='edit-account'),
]

from django.urls import path

from .views import edit_account_info, edit_payment_info, create_stellar_account
#albedo_get_public_key

urlpatterns = [
    path('edit-account/', edit_account_info, name='edit-account'),
    path('edit-payment-info/', edit_payment_info, name='edit-payment-info'),
    path('edit-payment-info/create-account-stellar', create_stellar_account, name='create-account-stellar'),
#    path('albedo-public-key/', albedo_get_public_key, name='albedo-public-key'),
]

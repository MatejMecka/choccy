from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from accounts.forms import ChangeUserInfo, ChangeStellarPublicKey, StellarPrivateKeyForm
from accounts.models import CustomUser, StellarAccount
from django.shortcuts import redirect
from .utils import generateAccount, getClaimableBalance, claimBalance

# Create your views here.
@login_required
def edit_account_info(request):
    if request.method == 'POST':
        form = ChangeUserInfo(request.POST)
        if form.is_valid():
            messages.success(request, "Account data updated!")
        else:
            messages.warning(request, form.errors)
            print(form.errors)
    else:
        data = CustomUser.objects.get(username=request.user.username)
        form = ChangeUserInfo(instance=request.user)
    return render(request, 'account/edit_account.html', {'form': form})

@login_required
def edit_payment_info(request):
    try:
        data = StellarAccount.objects.get(accountId=request.user)
    except StellarAccount.DoesNotExist:
        data = None

    if request.method == 'POST':
        form = ChangeStellarPublicKey(request.POST)
        if form.is_valid():
            messages.success(request, "Payment information updated!")
        else:
            messages.warning(request, form.errors)
    else:
        try:
            form = ChangeStellarPublicKey(instance=data)
        except:
            form = ChangeStellarPublicKey()
    return render(request, 'account/edit_payment_information.html', {'form': form, 'public_key': data})

"""
@csrf_exempt # Probably not a Good idea but it's a hackathon so...
def albedo_get_public_key(request):
    if request.method == 'POST':
        print(request.user)
        if not request.user.is_anonymous:
            data = request.POST
            public_key = data["pubkey"]
            account = StellarAccount.objects.get(accountId=request.user)
            if account.exists():
                account.public_key = public_key
            else:
                account = StellarAccount.objects.create(accountId=request.user, public_key=public_key)
            account.save()
            return HttpResponse(data)
        else: 
            return HttpResponseForbidden()
    else:
        return HttpResponseBadRequest('Not supporting get')
"""
@login_required
def create_stellar_account(request):
    if request.method == 'POST':
        try:
            account = StellarAccount.objects.get(accountId=request.user)
            messages.warning(request, "Account already exists!")
        except StellarAccount.DoesNotExist:
            account = generateAccount()
            return render(request, 'account/account_made.html', {'keys': account})

    form = ChangeStellarPublicKey()
    return render(request, 'account/edit_payment_information.html', {'form': form})

def claim_balance(request, balance_id):
    form = StellarPrivateKeyForm()
    if request.method == 'POST':
        form = StellarPrivateKeyForm(request.POST)
        if form.is_valid():
            balance_info = getClaimableBalance(balance_id)
            if balance_info["asset"] == "native":
                status, url = claimBalance(balance_id, form.data["private_key"])
                print(url)
                messages.success(request, f'Transaction Succeded! View it at {url}')
        else:
            print(form.errors)
            messages.warning(request, form.errors)
            
    return render(request, 'account/claim_balance.html', {'form': form})
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, Http404
from accounts.forms import ChangeUserInfo, ChangeStellarPublicKey, StellarPrivateKeyForm, EditProfile, PaymentForm
from accounts.models import CustomUser, StellarAccount, PublicProfile
from django.shortcuts import redirect
from .utils import generateAccount, getClaimableBalance, claimBalance, verifyItExists, getAssets, createClaimableBalance
from .choices import ASSET_HASHMAP

# Create your views here.
@login_required
def edit_account_info(request):
    if request.method == 'POST':
        form = ChangeUserInfo(request.POST)
        if form.is_valid():
            user = CustomUser.objects.get(username=request.user.username)
            f = ChangeUserInfo(request.POST, instance=user)
            f.save()
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
            StellarAccount.objects.create(accountId=request.user, public_key=account['public_key'])
            return render(request, 'account/account_made.html', {'keys': account})

    form = ChangeStellarPublicKey()
    return render(request, 'account/edit_payment_information.html', {'form': form})

def claim_balance(request, balance_id):
    form = StellarPrivateKeyForm()
    establishTrustline = False

    balance_info = getClaimableBalance(balance_id)
    if balance_info["asset"][0] == "native":
        balance_info["asset"][0] = 'XLM'
        establishTrustline = False
    else:
        # This is kids why you need to learn about Hash Maps <3
        account = StellarAccount.objects.get(accountId=request.user).public_key
        for asset in getAssets(account):
            if asset['asset_code'] == balance_info["asset"][0] and asset['issuer'] == balance_info["asset"][1]:
                print(asset['asset_code'] + '\t' + balance_info["asset"][0])
                establishTrustline = False
                break
            else:
                establishTrustline = True
           

    if request.method == 'POST':
        form = StellarPrivateKeyForm(request.POST)
        if form.is_valid():
            try:
                balance_info = getClaimableBalance(balance_id)
                if not establishTrustline:
                    status, url = claimBalance(balance_id, form.data["private_key"])
                else:
                    status, url = claimBalance(balance_id, form.data["private_key"], balance_info["asset"][0], balance_info["asset"][1])

                print(url)
                if status == True:
                    messages.success(request, f'Transaction Succeded! View it at {url}')
                else:
                    messages.warning(request, f'Transaction Failed! {url}')
            except Exception as e:
                
                messages.warning(request, f'Something went wrong. {e}')
        else:
            print(form.errors)
            messages.warning(request, form.errors)

    return render(request, 'account/claim_balance.html', {'form': form, 'establishTrustline': establishTrustline, 'balance_info': balance_info})

@login_required
def edit_profile_page(request):
    try:
        data = PublicProfile.objects.get(accountId=request.user.id)
    except PublicProfile.DoesNotExist:
        data = None

    if request.method == 'POST':
        form = EditProfile(request.POST)
        if form.is_valid():
            print(request.user.id)
            try:
                user = PublicProfile.objects.get(accountId=request.user.id)
                f = EditProfile(request.POST, instance=user)
            except PublicProfile.DoesNotExist:
                data = form.data
                f = PublicProfile.objects.create(accountId=CustomUser.objects.get(username=request.user.username), 
                    short_description=data["short_description"],
                    description=data["description"],
                    twitter_profile=data["twitter_profile"],
                    image_url=data["image_url"]
                )
                f.save()

            messages.success(request, "Account data updated!")
        else:
            messages.warning(request, form.errors)
            print(form.errors)
    else:
        form = EditProfile(instance=data)
    return render(request, 'account/edit_profile_page.html', {'form': form})

def view_user(request, username):
    user = None
    desination = None
    try:
        user = CustomUser.objects.get(username=username)
        public_info = PublicProfile.objects.get(accountId=user.id)
        
        destination = StellarAccount.objects.get(accountId=user.id).public_key

    except CustomUser.DoesNotExist:
        Http404("User not found")
    except StellarAccount.DoesNotExist:
        Http404("Payment Method not setup")


    form = PaymentForm()
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            data = form.data
            private_key = data["private_key"]
            amount = data["amount"]
            print(ASSET_HASHMAP.get(data["asset"]))
            if data["asset"] == 'native':
                status, url = createClaimableBalance(private_key, destination, amount)
                if status == True:
                    messages.success(request, f"Transaction Succeded! View it at {url}")
                else:
                    messages.error(request, f'Something went wrong. {url}')
            elif ASSET_HASHMAP.get(data["asset"]) is not None:
                asset_name = ASSET_HASHMAP.get(data["asset"])
                asset_issuer = data["asset"]

                print(asset_name)
                print(asset_issuer)

                status, url = createClaimableBalance(private_key, destination, amount, asset_name, asset_issuer)
                print(status)
                if status == True:
                    messages.success(request, f'Transaction Succeded! View it at {url}')
                else:
                    messages.error(request, f'Transaction failed: {url}')
            else:
                if data["asset_name"] == None or data["asset_issuer"] == None:
                    messages.error(request, f'Asset Name or Asset Issuer should not be empty!')
                else:
                    status, url = createClaimableBalance(private_key, destination, amount, data["asset_name"], data["asset_issuer"])
                    print(status)
                    if status == True:
                        messages.success(request, f'Transaction Succeded! View it at {url}')
                    else:
                        messages.error(request, f'Transaction failed: {url}')


    return render(request, 'account/user_profile.html', {"user": user, "public_info": public_info, "form": form})
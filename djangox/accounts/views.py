from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.forms import ChangeUserInfo
from accounts.models import CustomUser

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
        data = CustomUser.objects.get(username=request.user.username).__dict__
        form = ChangeUserInfo(initial=data)
    return render(request, 'account/edit_account.html', {'form': ChangeUserInfo})
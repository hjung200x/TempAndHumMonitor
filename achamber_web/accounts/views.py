from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages, auth
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def AccountsChangePassword(request):
    if request.method == "POST":
        user = request.user
        origin_password = request.POST.get('origin_password')
        if check_password(origin_password, user.password):
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return HttpResponseRedirect(reverse('index'))
            else:
                messages.error(request, 'Password not same')
        else:
            messages.error(request, 'Password not correct')
        return render(request, 'change_password.html')
    else:
        return render(request, 'change_password.html')

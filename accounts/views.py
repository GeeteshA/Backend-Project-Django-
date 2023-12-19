from django.shortcuts import render
from cmath import log
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from .models import Profile

# Create your views here.

def login_page(request):
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user_obj = User.objects.filter(username = email)

            if not user_obj.exists():
                messages.warning(request, 'Account not found.')
                return HttpResponseRedirect(request.path_info)
            
            if  not user_obj[0].profile.is_email_varified:
                 messages.warning(request,'Your account is not varified')
                 return HttpResponseRedirect(request.path_info)

            user_obj = authenticate(username = email , password = password)
            if user_obj:
                login(request , user_obj)
                return redirect('/')
            
            messages.warning(request, 'Invalid credentials')
            return HttpResponseRedirect(request.path_info)
        return render(request ,'accounts/login.html')



def activate_email(request , email_token):
     try:
          user = Profile.objects.get(email_token = email_token)
          user.is_email_varified = True
          user.save()
          return redirect('/')
     except Exception as e:
          return HttpResponse('Invalid Email token')
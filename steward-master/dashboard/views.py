from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic
from django.db.models import Q
from django.contrib import messages 
from django.contrib.auth.models import User


class EmptyDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/empty.html"


class VoipDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/voip.html"

class HomeDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

class Registration(generic.View):
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request,'dashboard/register.html')

    
    def post(self,request):
        try:
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            if User.objects.filter(Q(username=username)| Q(email=email)).exists():
                messages.error(request,'User with this email or username already exist')
                return redirect('/dashboard/register')
            else:
                User.objects.create(username=username,email=email,password=password)
                messages.success(request,'Successfully Created user.')
                return redirect('/accounts/login')
        except Exception as e:
            print(e)
            messages.error(request,'An error occurred. Please fill the form properly')
            return redirect('/dashboard/register')
            
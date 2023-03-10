from django.shortcuts import render, redirect
from django.views.generic import CreateView
from .models import User
from .forms import ClubRepSignUpForm, StudentSignUpForm, CinemamanagerSignUpForm, AccountmanagerSignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin


def home(request):
    return render(request, 'accounts/home.html')

def perm_denied(request):
    return render(request, 'accounts/no_perm.html')

#handles permissions(blocks users and redirects to 404 page if user is not authorized)
class UserAccessMixin(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if (not self.request.user.is_authenticated):
            return redirect('/login')
          
        if not self.has_permission():
            return redirect('/404')
        return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)


class student_register(UserAccessMixin,CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'accounts/student_register.html'
    success_url = "/"

    raise_exception = True
    permission_required = 'accounts.add_student'
  

class clubrep_register(UserAccessMixin,CreateView):
    model = User
    form_class = ClubRepSignUpForm
    template_name = 'accounts/clubrep_register.html'
    success_url = "/"

    raise_exception = True
    permission_required = 'accounts.add_clubrep'
    #permission_denied_message = ""
    #login_url = '/login/'
    #redirect_field_name = 'next'

    
class cinemamanager_register(UserAccessMixin,CreateView):
    model = User
    form_class = CinemamanagerSignUpForm
    template_name = 'accounts/cinemamanager_register.html'
    success_url = "/"

    raise_exception = True
    permission_required = 'accounts.add_cinemamanager'

  
class accountmanager_register(UserAccessMixin,CreateView):
    model = User
    form_class = AccountmanagerSignUpForm
    template_name = 'accounts/accountmanager_register.html'
    success_url = "/"

    raise_exception = True
    permission_required = 'accounts.add_accountmanager'



def login_request(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == "POST":
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request,user)
                    return redirect('/')
                else:
                    messages.error(request, "Invalid username or password")
            else:
                messages.error(request, "Invalid username or password")
        return render(request, 'accounts/login.html', context={'form' :AuthenticationForm()})


def logout_view(request):
    logout(request)
    return redirect('/')
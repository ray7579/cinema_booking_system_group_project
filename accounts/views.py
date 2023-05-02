from django.shortcuts import render, redirect
from django.views.generic import CreateView
from .models import User, Student, ClubRep, CinemaManager, AccountManager
from .forms import ClubRepSignUpForm, StudentSignUpForm, CinemamanagerSignUpForm, AccountmanagerSignUpForm, userForm, StudentUpdateForm, ClubrepUpdateForm, AccountmanagerUpdateForm, CinemamanagerUpdateForm
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import UpdateView


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


def accountshome(request):
    users = User.objects.order_by('username')
    return render(request, 'accounts/accountslist.html', {'users': users})


def updateuser(request, user_id):
    user = User.objects.get(id=user_id)
    form = userForm(request.POST or None, instance=user)

    if user.is_student:
        temp = Student.objects.get(user=user_id)
        tempform = StudentUpdateForm(request.POST or None, instance=temp, initial={
                'credit':temp.credit,})
      

    if user.is_clubrep:
        temp = ClubRep.objects.get(user=user_id)
        tempform = ClubrepUpdateForm(request.POST or None, instance=temp, initial={
                'clubname':temp.clubname,
                'street_no': temp.street_no,
                'street': temp.street, 
                'city': temp.city, 
                'postcode': temp.postcode, 
                'landline_no': temp.landline_no, 
                'mobile_no': temp.mobile_no, 
                'credit': temp.credit,})
        
    if user.is_accountmanager or user.is_cinemamanager:
        tempform = None

    if user.is_accountmanager:
        temp = AccountManager.objects.get(user=user_id)
        tempform = AccountmanagerUpdateForm(request.POST or None, instance=temp, initial={

                })
    if user.is_cinemamanager:
        temp = CinemaManager.objects.get(user=user_id)
        tempform = CinemamanagerUpdateForm(request.POST or None, instance=temp, initial={

                })


      

    if form.is_valid() and tempform.is_valid():
        form.save()
        tempform.save()
        print("saving form")
        return redirect(accountshome)

    return render(request, 'accounts/updateuser.html', {'form': form, 'tempform': tempform})


def deleteuser(request, user_id):
    deleting = User.objects.get(id=user_id)
    deleting.delete()
    return redirect(accountshome)
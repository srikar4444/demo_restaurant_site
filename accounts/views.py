from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from .forms import LoginForm, RegisterForm, GuestForm
from django.utils.http import is_safe_url
from .models import GuestEmail
from django.views.generic import CreateView, FormView
from .signals import user_logged_in
# Create your views here.


class LoginView(FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = "accounts/login.html"

    def form_valid(self,form):

        request = self.request
        next_get = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_get or next_post or None

        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # the below line code is used in analytics to check the user activity
            user_logged_in.send(user.__class__,instance = user,  request = request)
            try:
                del request.session['guest_email_id']
            except:
                pass
            if (is_safe_url(redirect_path, request.get_host())):
                return redirect(redirect_path)
            else:
                # context['form'] = LoginForm()
                return redirect("/")

        return super(LoginView,self).form_invalid(form)

""""
def login_page(request):
    form = LoginForm(request.POST or None)
    context = {
        "form": form
    }
    #print("User logged in")
    print(request.user.is_authenticated)
    # to send the user to the links after login
    next_get    = request.GET.get('next')
    next_post   = request.POST.get('next')
    redirect_path = next_get or next_post or None
    if (form.is_valid()):
        #print("Hi ")
        print(form.cleaned_data)
        context['form'] = LoginForm()

        username    = form.cleaned_data.get("username")
        password    = form.cleaned_data.get("password")
        user        = authenticate(request,username= username, password = password)

        #print(request.user.is_authenticated)
        print(user)
        if user is not None:
            #print(request.user.is_authenticated)
            #print("Hello")
            login(request,user)
            try:
                del request.session['guest_email_id']
            except:
                pass
            if(is_safe_url(redirect_path, request.get_host())):
                return redirect(redirect_path)
            else:
                #context['form'] = LoginForm()
                return redirect("/")
        else:
            print("Error")
"""

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = "/login/"

"""
# commented after using CreateView library
User = get_user_model()
def register_page(request):
    form = RegisterForm(request.POST or None)
    context = {
        "form" : form
    }
    if (form.is_valid()):
        form.save()

        # commented after changing the RegisterForm according to UserAdminCreationForm
        #print(form.cleaned_data)
        #username        = form.cleaned_data.get("username")
        #email           = form.cleaned_data.get("email")
        #password        = form.cleaned_data.get("password")
        #new_user        = User.objects.create_user(username,email,password)
        #print(new_user)

    return render(request,"accounts/register.html",context)
"""

def guest_register_view(request):
    form = GuestForm(request.POST or None)
    context = {
        "form": form
    }
    #print("User logged in")
    print(request.user.is_authenticated)
    # to send the user to the links after login
    next_get    = request.GET.get('next')
    next_post   = request.POST.get('next')
    redirect_path = next_get or next_post or None
    if (form.is_valid()):
        email                   = form.cleaned_data.get("email")
        new_guest_email         = GuestEmail.objects.create(email = email)
        request.session['guest_email_id'] = new_guest_email.id
        if(is_safe_url(redirect_path, request.get_host())):
            return redirect(redirect_path)
        else:
            #context['form'] = LoginForm()
            return redirect("/register/")

    return render("/register/")



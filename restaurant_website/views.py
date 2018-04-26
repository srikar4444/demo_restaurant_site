from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from .forms import ContactForm

def home_page(request):
    #print(request.session.get("first_name","Unknown")) #getter
    # request.session['first_name'] # same as above but gives error if it doesnot exist
    #return HttpResponse(home_page)
    context = {
        "title" : "Home page",
        "content" : "Welcome to Home page!"

    }
    if (request.user.is_authenticated):
        context["premium_content"] = "You are a premium member"
    return render(request,"home_page.html",context)

def about_page(request):
    context = {
        'title' : 'About page',
        'content': 'Welcome to About page!'
    }
    return render(request,"home_page.html",context)

def contact_page(request):
    contact_form = ContactForm(request.POST or None)
    context = {
        "title" : "Contact page",
        "content": "Welcome to Contact page!",
        "forms" : contact_form
    }
    if (contact_form.is_valid()):
        if (request.is_ajax()):
            return JsonResponse({"message": "Thank you for your Contacting us :D. We will get back to you :D"})
        print(contact_form.cleaned_data)
    if (contact_form.errors):
        errors = contact_form.errors.as_json()
        if (request.is_ajax()):
            # already errors is in json so we return that as HttpResponse
            return HttpResponse(errors, status = 400, content_type = "application/json")

    #if (request.method=="POST"):
    #    print(request.POST)
    #    print(request.POST.get('fullname'))
    #    print(request.POST.get('email'))

    return render(request,"contact/view.html",context)

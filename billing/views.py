from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url
from .models import BillingProfile, Card
# Create your views here.
import stripe
# need to change the default key value to proper default value
STRIPE_SECRET_KEY   = getattr(settings,"STRIPE_SECRET_KEY",'sk_test_AAAAAAAAAAAA')
STRIPE_PUB_KEY      = getattr(settings,"STRIPE_PUB_KEY", 'pk_test_AAAAAAAAAAAAA')
stripe.api_key = STRIPE_SECRET_KEY

def payment_method_view(request):
    #if request.method == "POST":
    #    print(request)
    #if request.user.is_authenticated:
    #    billing_profile = request.user.billingProfile
    #    my_customer_id = billing_profile.customer_id
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        # returning the user to cart if the billingprofile is not created
        return redirect("/cart")
    next_url = None
    next_get = request.GET.get('next')
    if (is_safe_url(next_get, request.get_host())):
        next_url = next_get

    return render(request, 'billing/payment-method.html',{"publish_key": STRIPE_PUB_KEY, "next_url" : next_url})

def payment_method_createview(request):
    print("hello")
    if ((request.method == "POST") and (request.is_ajax())):
        # returning the guest user to cart if the billingprofile is not created
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        print(request.POST)
        if not billing_profile:
            return HttpResponse({"message": "Cannot find this user"},status_code = 401)

        # "token" is mentioned in ecommerce.main.js
        token = request.POST.get("token")
        # below two lines of code taken from stripe website create card and modified
        if token is not None:
            print("customer_id in views: ",billing_profile.customer_id)
            #customer = stripe.Customer.retrieve(billing_profile.customer_id)
            #card_response = customer.sources.create(source=token)
            #new_card_obj = Card.objects.add_new(billing_profile, card_response)
            new_card_obj = Card.objects.add_new(billing_profile, token)
            #print(card_response) # start saving our cards too
            print(new_card_obj)
            return JsonResponse({"message":"Success! Your card is added."})
    return HttpResponse("error", status_code = 401)
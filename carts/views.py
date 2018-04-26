from django.shortcuts import render, redirect
from django.conf import settings
from .models import Cart,CartManager
from products.models import Product
from orders.models import Order
from accounts.forms import LoginForm, GuestForm
from billing.models import BillingProfile
from addresses.forms import AddressForm
from addresses.models import Address
from accounts.models import GuestEmail
from django.http import JsonResponse
import decimal
import stripe
# need to change the default value to proper default value for the stripe keys
STRIPE_SECRET_KEY   = getattr(settings,"STRIPE_SECRET_KEY",'sk_test_AAAAAAAAAAAAAAAAAA')
STRIPE_PUB_KEY      = getattr(settings,"STRIPE_PUB_KEY", 'pk_test_AAAAAAAAAAAAAAAAAA')
stripe.api_key = STRIPE_SECRET_KEY
# Create your views here.

def cart_create(user=None):
    cart_obj = Cart.objects.create(user=None)
    print('New Cart created ')
    return cart_obj

def cart_home(request):
    """
    #print(request.session)
    #print(dir(request.session))
    # request.session.set_expiry(300) #300 seconds ie 5 minutes only input in seconds
    # request.session.session_key
    #key = request.session.session_key
    #print(key)
    #request.session['first_name'] = "Justin" #setter

    #del request.session['cart_id']
    #request.session['cart_id'] = "12"
    cart_id = request.session.get("cart_id",None)
    # isinstance to check whatever is coming is an integer
    #if cart_id is None: # and isinstance(cart_id, int):
    #    cart_obj = cart_create()
    #    request.session['cart_id'] = cart_obj.id

    #request.session['cart_id'] = 121 #setter
    #else:
    qs = Cart.objects.filter(id=cart_id)
    #if not qs.exists() and qs.count() == 1:
    if qs.count() ==1:
        cart_obj = qs.first()
        print('Cart ID exists')
        if request.user.is_authenticated and cart_obj.user is None:
            cart_obj.user = request.user
            cart_obj.save()
    else:
        #cart_obj = cart_create()
        #the below line will call the new method in CartManager class
        cart_obj = Cart.objects.new(user=request.user)
        #print(cart_id)
        #cart_obj = Cart.objects.get(id=cart_id)
        request.session['cart_id'] = cart_obj.id
    return render(request,"carts/home.html",{})
    """
    # from here we will be using new_or_get method we created in CartManager class
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    #products = cart_obj.products.all()
    #total = float(0.0)
    #for x in products:
    #    total = total + float(x.price)
    #print(total)
    #cart_obj.total = decimal.Decimal(total)
    #cart_obj.save()
    return render(request,"carts/home.html",{"cart":cart_obj})

def cart_update(request):
    print(request.POST)

    # product_id is the 'name' val in update-cart.html which takes the value of the product.id
    product_id = request.POST.get('product_id')
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Show message to user, Product is gone?")
            return redirect("carts:home")
        cart_obj , new_obj = Cart.objects.new_or_get(request)
        if (product_obj in cart_obj.products.all()):
            cart_obj.products.remove(product_obj)
            # to keep a track if the product is added to cart or not
            added = False
        else:
            cart_obj.products.add(product_obj) #cart_obj.products.add(product_id)
            added = True
    # cart_obj.products.remove(product_obj) # cart_obj.products.remove(product_id)
    #return redirect(product_obj.get_absolute_url())
    request.session['cart_items'] = cart_obj.products.count()
    # this code is written here because if the user disables js or xml in browser this webpage should work so it uses
    # the above code directly and returns finally.
    if (request.is_ajax()):
        # if the request is in ajax (Asynchronous JavaScript and XML) form then do some similar things but not same things
        # like returning data using JSON
        print("Ajax request")
        # not added takes value opposite of added
        json_data = {
            "added" : added,
            "removed" : not added,
                "cartItemCount" : cart_obj.products.count()
        }
        return JsonResponse(json_data,status = 200)
        # below code is just for checking the error display
        #return JsonResponse({"message":"Error 400"}, status = 400) # Django rest framework can do better work
    return redirect("carts:home")

def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    # get_or_create() is a default method in django
    order_obj = None
    # if cart is newly created or cart has zero products added in it then it should be shown by cart home view not checkout
    if cart_created or cart_obj.products.count()==0:
        return redirect("cart:home")
    #else:
        #order_obj, new_order_obj = Order.objects.get_or_create(cart= cart_obj)
    #user =request.user
    #billing_profile = None
    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()
    billing_address_id = request.session.get("billing_address_id",None)
    shipping_address_id = request.session.get("shipping_address_id",None)
    #billing_address_form = AddressForm()
    guest_email_id = request.session.get('guest_email_id')
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    """
    # the below code is written in BillingProfile manager in new_or_get function
    if user.is_authenticated:
        # logged in user checkout, remembers payment stuff
        #if user.email:
            # get_or_create is a function which returns the object created and also it returns a boolean if a new
            # object is created or not its of the below form
            # obj, bool = get_or_create(..)
        billing_profile, billing_profile_created = BillingProfile.objects.get_or_create(user = user, email = user.email)
    elif guest_email_id is not None:
        # guest user checkout, auto reload of payment stuff
        guest_email_obj = GuestEmail.objects.get(id = guest_email_id)
        billing_profile, billing_profile_created = BillingProfile.objects.get_or_create(email=guest_email_obj.email)
    else:
        pass
    """
    # the above order creation is for logged in users
    # the below one is when the user is going with guest email and then going through register and again order it
    address_qs = None
    has_cards = False # check for any added cards
    if billing_profile is not None:
        if (request.user.is_authenticated):
            #option to select address from the list of previous addresses
            address_qs = Address.objects.filter(billing_profile = billing_profile)
        #shipping_address_qs = address_qs.filter(address_type = 'shipping')
        #billing_address_qs = address_qs.filter(address_type='billing')
        # new_or_get is a custom made function in orders/models.py in OrderManager
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]
            if not billing_profile.user:
                #when the user is in guest all the cards are made inactive so that he dont use others cards
                    billing_profile.set_cards_inactive()
        if billing_address_id or shipping_address_id:
            order_obj.save()
        #order_qs = Order.objects.filter(billing_profile= billing_profile,cart = cart_obj,active = True)
        #if order_qs.count() ==1:
        #    order_obj = order_qs.first()
            #order_qs.update(active= False)
        #else:
            # everytime we login logout it is creating a new billing profile and storing them but we don't want to save them
            # we have to delete them, so it is stored in old_order_qs and deleted excluding the current one
            #old_order_qs = Order.objects.exclude(billing_profile = billing_profile).filter(cart = cart_obj, active = True)
            #if (old_order_qs.exists()):
            #    old_order_qs.update(active= False)
        #    order_obj = Order.objects.create(billing_profile= billing_profile, cart= cart_obj)
    # no need of the billing_address_form as it will be considered from the instance address only
    # things to be done after billing addresss is filled is 1. update order_obj to done, "paid",
    # 2. del request.session['cart_id']  3.redirect "success"

        has_cards = billing_profile.has_card #checking for any saved cards


    if request.method=="POST":
        # "some check that order is done"
        is_prepared = order_obj.check_done()

        if (is_prepared):
            did_charge, crg_msg = billing_profile.charge(order_obj)
            if did_charge:
                #making the cart_items as 0 , deleting the cart id and redirecting
                order_obj.mark_paid()
                request.session['cart_items'] = 0
                del request.session['cart_id']
                return redirect('carts:success')
            else:
                print(crg_msg)
                return redirect('carts:checkout')
    context = {
        "object": order_obj,
        "billing_profile" : billing_profile,
        "login_form" : login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
        #"billing_address_form" : billing_address_form,
        "has_card" : has_cards,
        "publishKey" : STRIPE_PUB_KEY,
    }
    return render(request, "carts/checkout.html", context)

def checkout_done_view(request):
    return render(request, "carts/checkout_done.html",{})

def cart_detail_api_view(request):
    # this function is used when javascript is present and it will be called instead of cart_update
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    #products = cart_obj.products.all() # this returns the form [<object>, <object>, <object>]
    products = [{
                "id" : x.id,
                "url" : x.get_absolute_url(),
                "name": x.name,
                "price": x.price
                }
                for x in cart_obj.products.all()]
    # the above products thing is same sa
    # products_list = []
    # for x in cart_obj.products.all():
    #   products_list.append(
    #        {"name": x.name, "price": x.price}
    #   )
    cart_data = {
        "products" : products,
        "subtotal" : cart_obj.subtotal,
        "total" : cart_obj.total
    }
    return JsonResponse(cart_data)
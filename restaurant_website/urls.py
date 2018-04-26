"""restaurant_website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from carts.views import cart_home
from addresses.views import checkout_address_create_view, checkout_address_reuse_view
from carts.views import cart_detail_api_view

from marketing.views import MarketingPreferenceUpdateView, MailChimpWebHookView
from accounts.views import LoginView, guest_register_view, RegisterView #register_page, login_page,
from .views import home_page,about_page,contact_page
from billing.views import payment_method_view, payment_method_createview

#from products.views import (ProductListView,
#                            product_list_view,
#                            ProductDetailView,
#                            product_detail_view,
#                            ProductFeaturedListView,
#                            ProductFeaturedDetailView,
#                            ProductDetailSlugView
#                            )

urlpatterns = [
    path('',home_page,name='home'),
    path('about/',about_page,name='about'),
    path('contact/',contact_page,name='contact'),
    path('admin/', admin.site.urls),
    #path('login/',login_page,name='login'),
    path('login/',LoginView.as_view(),name='login'),
    path('checkout/address/create',checkout_address_create_view,name='checkout_address_create'),
    path('checkout/address/reuse',checkout_address_reuse_view,name='checkout_address_reuse'),
    path('register/guest', guest_register_view, name="guest_register"),
    path('logout/',LogoutView.as_view() ,name='logout'),
    #path('register/',register_page,name='register'),
    path('billing/payment-method/',payment_method_view,name='billing-payment-method'),
    path('billing/payment-method/create/',payment_method_createview,name='billing-payment-method-endpoint'),
    path('register/',RegisterView.as_view(),name='register'),
    path('products/',include(("products.urls","products"),namespace='products')),
    path('search/',include(("searchapp.urls","searchapp"),namespace='search')),
    path('settings/email/',MarketingPreferenceUpdateView.as_view(), name='marketing-pref'),
    path('webhooks/mailchimp/',MailChimpWebHookView.as_view(), name='webhooks-mailchimp'),
    path('api/cart/',cart_detail_api_view,name='api-cart'),
    path('cart/',include(("carts.urls","carts"),namespace='carts')),

    #path('bootstrap/',TemplateView.as_view(template_name="bootstrap/example.html")),

    #path('products/',ProductListView.as_view()),
    #path('products-fbv/',product_list_view,name='product-fbv'),
    #path('products/<pk>/',ProductDetailView.as_view()),
    #path('products-fbv/<pk>/', product_detail_view, name='product-fbv-detail'),
    #path('featured/',ProductFeaturedListView.as_view()),
    #path('featured/<pk>/',ProductFeaturedDetailView.as_view()),
    #path('products/<slug>/',ProductDetailSlugView.as_view()),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL,document_root = settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
from django.db import models
from django.db.models.signals import pre_save, post_save
import math
import decimal
# Create your models here.
from billing.models import BillingProfile
from addresses.models import Address
from carts.models import Cart
from restaurant_website.utils import unique_order_id_generator

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped','Shipped'),
    ('refunded','Refunded'),
    ('cancelled','Cancelled'),
    )

class OrderManager(models.Manager):
    def new_or_get(self,billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(billing_profile = billing_profile, cart = cart_obj, active = True,status ='created')
        if qs.count()==1:
            created = False
            obj = qs.first()
        else:
            obj = self.model.objects.create(billing_profile = billing_profile, cart = cart_obj)
            created = True
        return obj, created

class Order(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE, null=True, blank=True)
    order_id            = models.CharField(max_length=120, blank=True)  # ex:-  ABX090D
    # as there are two foreign keys from the same class the django gets confused so we need to use related_name attribute
    billing_address     = models.ForeignKey(Address,related_name="shipping_address", null=True, blank=True, on_delete=models.CASCADE)
    shipping_address    = models.ForeignKey(Address,related_name="billing_address",null=True, blank=True, on_delete=models.CASCADE)
    cart                = models.ForeignKey(Cart,on_delete= models.CASCADE)
    status              = models.CharField(max_length=120, default='created',choices=ORDER_STATUS_CHOICES)
    shipping_total      = models.DecimalField(default= 5.99, max_digits=20, decimal_places=2)
    total               = models.DecimalField(default= 5.99, max_digits=20, decimal_places=2)
    active              = models.BooleanField(default=True)

    # for python 3 its str and for python 2 is unicode
    def __str__(self):
        return self.order_id

    objects = OrderManager()

    def __unicode__(self):
        return self.order_id

    def update_total(self):
        cart_total = self.cart.total
        shipping_total = self.shipping_total
        new_total = decimal.Decimal(0.0)
        # fsum is a python library to add decimal and float fields
        # the operands have to be passed in a list, it might give a lot of decimal places
        #new_total = math.fsum(cart_total + shipping_total)
        new_total = decimal.Decimal(cart_total) + decimal.Decimal(shipping_total)
        formatted_total = format(new_total,'.2f')
        self.total = formatted_total
        self.save()
        return new_total

    # Order id should be random and unique
    #generate order id
    # generate total
    # We can generate things from signals

    # function to check whether all the things in order are done like billing address profile and shipping address
    def check_done(self):
        billing_profile = self.billing_profile
        shipping_address = self.shipping_address
        billing_address = self.billing_address
        total = self.total
        if (self.total)<0:
            return False
        elif (billing_profile and shipping_address and billing_address and total>0):
            return True
        else:
            return False

    #  to mark order as paid after the payment
    def mark_paid(self):
        if self.check_done():
            self.status = "paid"
            self.save()
            return self.status


def pre_save_create_order_id(sender, instance , * args, ** kwargs):
    # we don't want to create the order_id once it is created
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
        # no need to call instance.save() as we are already using pre_save for that
    qs = Order.objects.filter(cart= instance.cart).exclude(billing_profile = instance.billing_profile)
    if (qs.exists()):
        qs.update(active = False)


pre_save.connect(pre_save_create_order_id, sender=Order)

def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_obj = instance
        #cart_total = cart_obj.total
        cart_id = cart_obj.id
        #notice the double underscore between cart and id, it actually takes the id's of carts
        qs = Order.objects.filter(cart__id = cart_id)
        if (qs.count() ==1):
            order_obj = qs.first()
            order_obj.update_total()

post_save.connect(post_save_cart_total,sender=Cart)

def post_save_order(sender, instance, created, *args, **kwargs):
    # we are checking if it is created or not so that we dont have to update it when not created or cart not changed
    print("running")
    if created:
        print("updating...!")
        instance.update_total()

post_save.connect(post_save_order, sender = Order)



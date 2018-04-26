from django.db import models
from django.conf import settings
from products.models import Product
from django.db.models.signals import pre_save, post_save, m2m_changed
import decimal



# Create your models here.

User = settings.AUTH_USER_MODEL

class CartManager(models.Manager):

    #there is already a method "get_or_create" which actually returns the obj and whether it is new or not
    # obj, True based on that the new_or_get is desgined

    def new_or_get(self,request):
        cart_id = request.session.get("cart_id",None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_obj = False
            cart_obj = qs.first()
            if request.user.is_authenticated and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            cart_obj = Cart.objects.new(user = request.user)
            new_obj= True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            if (user.is_authenticated):
                user_obj = user
        return self.model.objects.create(user=user_obj)

class Cart(models.Model):
    user        = models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    products    = models.ManyToManyField(Product,blank=True)
    subtotal    = models.DecimalField(default=0.00,max_digits=20, decimal_places=2)
    total       = models.DecimalField(default=0.00,max_digits=20, decimal_places=2)
    timestamp   = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    objects = CartManager()
    def __str__(self):
        return str(self.id)

def m2m_changed_cart_receiver(sender,instance,action, *args, **kwargs):
    #function to check the total value in cart
    # pre_save.connect or m2m_changed.connect are very important to update the cart value when the
    # cart products changes
    #print(action)
    #print(instance.products.all())
    #print(instance.total)

    if action=='post_add' or action=='post_remove' or action=='post_clear':
        products = instance.products.all()
        total =decimal.Decimal(0.0)
        for x in products:
            total += x.price
        #print(total)
        if instance.subtotal != decimal.Decimal(total):
            instance.subtotal = decimal.Decimal(total)
            instance.save()

#pre_save.connect(pre_save_cart_receiver,sender=Cart)
#check the documentation of m2m_changed for the below syntax
m2m_changed.connect(m2m_changed_cart_receiver,sender=Cart.products.through)

def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    #instance.total = instance.subtotal * decimal.Decimal(1.02)
    if (decimal.Decimal(instance.subtotal) > decimal.Decimal(0.0)):
        instance.total = decimal.Decimal(instance.subtotal) + decimal.Decimal(10.0)
    else:
        instance.total = decimal.Decimal(0.0)
pre_save.connect(pre_save_cart_receiver,sender=Cart)




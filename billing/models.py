from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
# Create your models here.
from django.urls import reverse
from accounts.models import GuestEmail


User = settings.AUTH_USER_MODEL

import stripe
# need to modify the default key to a proper default key
STRIPE_SECRET_KEY   = getattr(settings,"STRIPE_SECRET_KEY",'sk_test_AAAAAAA')
stripe.api_key = STRIPE_SECRET_KEY

class BillingProfielManager(models.Manager):
    def new_or_get(self,request):
        user = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated:
            # logged in user checkout, remembers payment stuff
            # if user.email:
            # get_or_create is a function which returns the object created and also it returns a boolean if a new
            # object is created or not its of the below form
            # obj, bool = get_or_create(..)
            obj, created = self.model.objects.get_or_create(user=user, email=user.email)
        elif guest_email_id is not None:
            # guest user checkout, auto reload of payment stuff
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(email=guest_email_obj.email)
        else:
            pass

        return obj, created



# email@gmail.com --> 1000000 billing profiles
# user email@gmail.com --> 1 billing profile
class BillingProfile(models.Model):
    # we can consider the billing as a Foreignkey with unique as True or just consider OneToOneField
    user        = models.OneToOneField(User,unique=True, null=True, blank= True,on_delete= models.CASCADE )
    email       = models.EmailField()
    active      = models.BooleanField(default=True)
    updated     = models.DateTimeField(auto_now_add=True)
    timestamp   = models.DateTimeField(auto_now_add=True )
    customer_id = models.CharField(max_length=200, null=True, blank = True)
    # customer_id in Stripe or Braintree

    objects = BillingProfielManager()
    def __str__(self):
        return self.email

    #def __unicode__(self):
    #    return self.customer_id

    def charge(self,order_obj, card = None):
        return Charge.objects.do(self, order_obj, card)

    def get_cards(self):
        return self.card_set.all()  # Card.objects.filter(billing_profiel = self) # ,active = True)

    def get_payment_method_url(self):
        return reverse('billing-payment-method') # return "billing/payment/method"

    @property
    def has_card(self):          # instance.has_card
        instance =  self
        card_qs = instance.card_set.all()
        return card_qs.exists() # either True or False

    @property
    def card_default(self):
        default_cards = self.get_cards().filter(active= True, default_card = True)
        if default_cards.exists():
            return default_cards.first()
        return None

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active = False)
        return cards_qs.filter(active =True).count()

def billing_profile_created_receiver(sender, instance , *args, **kwargs):
    # we take the customer id and his email and then send it to stripe for creating a customer obj
    print("customer creation ")
    if not instance.customer_id and instance.email:
        print("API REQUEST send to Stripe \ Braintree payment system")
        """  sending a request to stripe website inorder to get the user id
          All the third party requests will be done like this"""
        customer = stripe.Customer.create(
                email = instance.email,
            )
        print(customer)
        instance.customer_id = customer.id

pre_save.connect(billing_profile_created_receiver, sender=BillingProfile)

def user_created_receiver( sender, instance, created, *args, **kwargs):
    # we can also remove that instance.email thing
    if created and instance.email:
        BillingProfile.objects.get_or_create(user = instance, email =instance.email)


post_save.connect(user_created_receiver, sender=User)

# the card details that stripe produces
"""
<Card card id=card_1CHoLYELerKT6sdSFLPJUvdz at 0x00000a> JSON: {
  "id": "card_1CHoLYELerKT6sdSFLPJUvdz",
  "object": "card",
  "address_city": null,
  "address_country": null,
  "address_line1": null,
  "address_line1_check": null,
  "address_line2": null,
  "address_state": null,
  "address_zip": null,
  "address_zip_check": null,
  "brand": "Visa",
  "country": "US",
  "customer": "cus_ChClg7IUX8SvKj",
  "cvc_check": null,
  "dynamic_last4": null,
  "exp_month": 8,
  "exp_year": 2019,
  "fingerprint": "JaRhoxgDak5wOEzJ",
  "funding": "credit",
  "last4": "4242",
  "metadata": {
  },
  "name": null,
  "tokenization_method": null
}
"""

class CardManager(models.Manager):
    def all(self, *args, **kwargs):  #ModelKlass.objects.all() --> ModelKlass.objects.filter(active=True)
        return self.get_queryset().filter(active=True)


    #def add_new(self,billing_profile, stripe_card_response):
    def add_new(self, billing_profile, token):
        #if (str(stripe_card_response.object) == "card"):
        if token:
            if (billing_profile is None):
                print("billing_profile is none ")
            else :
                print("billing profile not none")
                print("user: ",billing_profile.user)
                print("email: ",billing_profile.email)
            print("cust_id:" , billing_profile.customer_id)
            customer = stripe.Customer.retrieve(billing_profile.customer_id)
            stripe_card_response = customer.sources.create(source=token)
            new_card = self.model( billing_profile = billing_profile,
                                   stripe_id = stripe_card_response.id,
                                   brand = stripe_card_response.brand,
                                   country = stripe_card_response.country,
                                   exp_month = stripe_card_response.exp_month,
                                   exp_year = stripe_card_response.exp_year,
                                   last4 = stripe_card_response.last4
                                  )
            new_card.save()
            return new_card
        return None

class Card(models.Model):
    billing_profile         = models.ForeignKey(BillingProfile, null=True,on_delete=models.CASCADE)
    stripe_id               = models.CharField(max_length=120, blank=False)
    brand                   = models.CharField(max_length=20, blank=True)
    country                 = models.CharField(max_length=20, blank=True)
    exp_month               = models.IntegerField(blank=False,null=False)
    exp_year                = models.IntegerField(blank=False,null=False)
    last4                   = models.CharField(max_length=4,blank=False)
    default_card            = models.BooleanField(default=True)
    active                  = models.BooleanField(default=True)
    timestamp               = models.DateTimeField(auto_now_add=True)


    objects = CardManager()

    def __str__(self):
        # format to return card details
        return "{} {}".format(self.brand, self.last4)

# once a new card is created and made default_card then all other cards are removed as default_cards
def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
    if (instance.default_card):
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(billing_profile = billing_profile).exclude(pk = instance.pk)
        qs.update(default_card = False)

post_save.connect(new_card_post_save_receiver, sender=Card)

class ChargeManager(models.Manager):
    # Charge.objects.do()
    def do(self,billing_profile, order_obj, card=None):
        card_obj = card
        if card_obj is None:
            cards = billing_profile.card_set.filter(default_card= True) # card_obj.billing_profile
            if cards.exists():
                card_obj = cards.first()
        if card_obj is None:
            return False, "No cards available"
        # the exceptions are not taken care here
        # the charg block should be in try block for different exceptions like time out and all
        # so for that just put look at the documentation in stripe

        charg = stripe.Charge.create(
            # the total should be multiplied by 100 in order to get the charge value
            # 39.19 to 3919
            amount = int(order_obj.total * 100),
            currency = "usd",
            customer = billing_profile.customer_id,
            source = card_obj.stripe_id,
            #description = "Charge for the 'xyz@gmail.com'"
            metadata = {"order_id": order_obj.order_id,},

        )
        new_charge_obj = self.model(
            billing_profile         = billing_profile,
            stripe_id               = charg.id,
            paid                    = charg.paid,
            refunded                = charg.refunded,
            outcome                 = charg.outcome,
            outcome_type            = charg.outcome['type'],
            seller_message          = charg.outcome.get('seller_message'),
            risk_level              = charg.outcome.get('risk_level')
        )
        new_charge_obj.save()
        return new_charge_obj.paid, new_charge_obj.seller_message


class Charge(models.Model):
    billing_profile         = models.ForeignKey(BillingProfile, null=True, on_delete=models.CASCADE)
    stripe_id               = models.CharField(max_length=120, blank=False)
    paid                    = models.BooleanField(default = False)
    refunded                = models.BooleanField(default=False)
    outcome                 = models.TextField(blank=True)
    outcome_type            = models.CharField(max_length=120, blank=True)
    seller_message          = models.CharField(max_length=120, blank=True)
    risk_level              = models.CharField(max_length=120, blank=True)

    objects = ChargeManager()
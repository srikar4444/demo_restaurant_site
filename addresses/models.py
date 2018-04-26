from django.db import models

from billing.models import BillingProfile
# we are going to associate addresses with billing profile
# we can do either with orders or billingprofile but for now we choose billingprofile
# Create your models here.

ADDRESS_TYPES =(
    ('billing','Billing'),
    ('shipping','Shipping'),
)

class Address(models.Model):
    billing_profile         = models.ForeignKey(BillingProfile,on_delete=models.CASCADE)
    address_type            = models.CharField(max_length=120, choices=ADDRESS_TYPES)
    address_line_1          = models.CharField(max_length=120)
    address_line_2          = models.CharField(max_length=120,null=True, blank=True)
    city                    = models.CharField(max_length=120)
    country                 = models.CharField(max_length=120,default = 'India')
    state                   = models.CharField(max_length=120)
    postal_code             = models.CharField(max_length=120)

    def __str__(self):
        return str(self.billing_profile)

    # this is used in carts/checkout.html to display the addresses after the order is finalized
    def get_address(self):
        return "{line1}\n{line2}\n{city}\n{state} : {postal}\n{country}".format(
            line1 = self.address_line_1,
            line2 = self.address_line_2 or "",
            city  = self.city,
            state  = self.state,
            postal = self.postal_code,
            country = self.country
        )
from django.contrib import admin

# Register your models here.
from .models import MarketingPreference

class MarketingPreferenceAdmin(admin.ModelAdmin):

    list_display = ['__str__','subscribed', 'updated']
    # comment this readonly_fields and check how they will change in the admin site
    # you cannot modify the data in the readonly_fields
    readonly_fields = ['mailchimp_msg', 'mailchimp_subscribed', 'timestamp','updated']
    class Meta:
        model = MarketingPreference
        fields = [
                    'user',
                    'subscribed',
                    'mailchimp_msg',
                    'mailchimp_subscribed',
                    'timestamp',
                    'updated'
                    ]

admin.site.register(MarketingPreference, MarketingPreferenceAdmin)
from django.shortcuts import render
# Create your views here.
from django.views.generic import UpdateView, View

from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import MarketingPreferenceForm
from .models import  MarketingPreference
from django.conf import settings
from .utils import MailChimp
from .mixins import CsrfExemptMixin

MAILCHIMP_EMAIL_LIST_ID = getattr(settings, "MAILCHIMP_EMAIL_LIST_ID", None)

class MarketingPreferenceUpdateView(SuccessMessageMixin,  UpdateView):
    form_class = MarketingPreferenceForm
    template_name = "basefiles/forms.html" # have to create this
    success_url = "/settings/email/"
    success_message = "Your email preferences have been updated. Thank you."

    def dispatch(self,  *args, **kwargs):
        # function to check whether the user has an account in the website
        # we cannot put this code in get_object directly because it was going for the main djangos function
        user = self.request.user
        if not user.is_authenticated:
            return redirect("/login/?next=/settings/email/")
            #return HttpResponse("Not allowed", status=400)
        return super(MarketingPreferenceUpdateView, self).dispatch(*args , **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(MarketingPreferenceUpdateView,self).get_context_data(*args, **kwargs)
        context['title'] = "Update Email Preferences"
        return context

    def get_object(self):
        user = self.request.user
        obj, created = MarketingPreference.objects.get_or_create(user = user) #get_absolute_url?
        return obj


"""
POST METHOD
data[web_id]: 3751217
data[email_type]: html
data[merges][EMAIL]: elephant@gmail.com
data[id]: 5621d2f820
type: subscribe
data[merges][ADDRESS]:
data[merges][LNAME]:
data[list_id]: 3a7f4c8d85
data[merges][PHONE]:
data[email]: elephant@gmail.com
data[merges][FNAME]:
fired_at: 2018-04-20 09:34:53
data[ip_opt]: 14.142.103.234
data[merges][BIRTHDAY]:
"""


class MailChimpWebHookView(CsrfExemptMixin, View):
    # HTTP GET -- def get() # use get instead of post
    # def get(self, request, *args, **kwargs):
        # get method is for testing
        # return HttpResponse("Thank you",status =200)


    # function to get the above kind of data from mailchimp when changes are done to our users
    # on the website regarding subscription
    # how to handle CSRF here?? its very important to not let requests from unknown sites to this
    def post(self, request, *args, **kwargs):
        data = request.POST
        list_id = data.get('data[list_id]')
        if (str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID)):
            hook_type = data.get('type')
            email = data.get('data[email]')
            response_status, response_data = MailChimp().check_subscription_status(email)
            sub_status = response_data['status']
            is_subbed = None
            mailchimp_subbed = None
            if (sub_status == "subscribed"):
                is_subbed, mailchimp_subbed = (True, True)
            elif (sub_status == "unsubscribed"):
                is_subbed, mailchimp_subbed = (False, False)
            if is_subbed is not None and mailchimp_subbed is not None:
                qs = MarketingPreference.objects.filter(user__email__iexact=email)
                if qs.exists():
                    qs.update(
                        subscribed=is_subbed,
                        mailchimp_subscribed=mailchimp_subbed,
                        mailchimp_msg=str(data)
                    )
        return HttpResponse("Thank you", status=200)


"""
This function is converted to class based function view
#function to get the above kind of data from mailchimp when changes are done to our users
# on the website regarding subscription
def mailchimp_webhook_view(request):
    data = request.POST
    list_id = data.get('data[list_id]')
    if (str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID)):
        hook_type = data.get('type')
        email = data.get('data[email]')
        response_status, response_data= MailChimp().check_subscription_status(email)
        sub_status = response_data['status']
        
        #if (sub_status == "subscribed" ):
        #    qs = MarketingPreference.objects.filter(user__email__iexact=email)
        #    if qs.exists():
        #        qs.update(subscribed = True,mailchimp_subscribed = True,mailchimp_msg = str(data) )
        #elif (sub_status=="unsubscribed"):
        #    qs = MarketingPreference.objects.filter(user__email__iexact=email)
        #    if qs.exists():
        #        qs.update(subscribed=False, mailchimp_subscribed = False, mailchimp_msg = str(data))
        
        is_subbed = None
        mailchimp_subbed = None
        if (sub_status=="subscribed"):
            is_subbed, mailchimp_subbed = (True, True)
        elif (sub_status == "unsubscribed"):
            is_subbed, mailchimp_subbed = (False, False)
        if is_subbed is not None and mailchimp_subbed is not None:
            qs = MarketingPreference.objects.filter(user__email__iexact=email)
            if qs.exists():
                qs.update(
                        subscribed = is_subbed,
                        mailchimp_subscribed = mailchimp_subbed,
                        mailchimp_msg =  str(data)
                        )

    return HttpResponse("Thank you",status = 200)
"""



import json
import hashlib # this is for hash values of strings/ emails
import re # this is for regular expression
import requests
# requests is a library and is installed using pip
from django.conf import settings
# http://developer.mailchimp.com/documentation/mailchimp/reference/lists/members/#%20
# important website to work with mailchimp

MAILCHIMP_API_KEY = getattr(settings, "MAILCHIMP_API_KEY",None)
MAILCHIMP_DATA_CENTER = getattr(settings, "MAILCHIMP_DATA_CENTER", None)
MAILCHIMP_EMAIL_LIST_ID = getattr(settings, "MAILCHIMP_EMAIL_LIST_ID", None)

# to check whether the given email is actually correct
def check_email(email):
    if not re.match(r".+@.+\..",email):
        raise ValueError('String passed is not a valid email address')
    return email

def get_subscribers_hash(member_email):
    check_email(member_email)
    member_email = member_email.lower().encode()
    m = hashlib.md5(member_email)
    return m.hexdigest()

class MailChimp(object):
    def __init__(self):
        super(MailChimp,self).__init__()
        self.key = MAILCHIMP_API_KEY
        #this is taken from the mail chimp website on using its api
        self.api_url = "https://{dc}.api.mailchimp.com/3.0/".format(dc = MAILCHIMP_DATA_CENTER)
        self.list_id = MAILCHIMP_EMAIL_LIST_ID

        # the website is the important thing as it tells us what to send
        # as the json data for sending emails through mail chimp
        self.list_endpoint = '{api_url}/lists/{list_id}'.format(
                                                api_url = self.api_url,
                                                list_id = self.list_id
                                            )


    def get_memebers_endpoint(self):
        return self.list_endpoint + "/members"

    def check_valid_status(self, status):
        choices = ['subscribed', 'unsubscribed', 'cleaned','pending']
        if status not in choices :
            raise ValueError("Not a valid choice for email status")
        return status

    # change the subscription status of the email
    def change_subscription_status(self, email, status="unsubscribed"):
        hashed_email = get_subscribers_hash(email)
        print(hashed_email)
        # GET /lists/{list_id}/members/{subscriber_hash}  should be in this format
        endpoint = self.get_memebers_endpoint() + "/" + hashed_email
        # we can put all the data that we want to change in this data dict
        data = {
            "status": self.check_valid_status(status)
        }
        r = requests.put(endpoint, auth=("", self.key),data = json.dumps(data))
        return r.status_code, r.json()
        #return r.json()

    # check the subscription status of the email
    def check_subscription_status(self, email):

        hashed_email = get_subscribers_hash(email)
        print(hashed_email)
        # GET /lists/{list_id}/members/{subscriber_hash}  should be in this format
        endpoint = self.get_memebers_endpoint() + "/"+ hashed_email
        r = requests.get(endpoint,auth=("",self.key))
        return r.status_code, r.json()


    def add_email(self, email):
        # the names in the data should be same as required by the mailchimp,
        # check the website for more info
        status = "subscribed"
        self.check_valid_status(status)
        data = {
            "email_address" : email,
            "status" : status,
        }
        endpoint = self.get_memebers_endpoint()
        r = requests.post(endpoint,auth=("",self.key),data= json.dumps(data))
        #return r.json()
        #return self.change_subscription_status(email,status='subscribed')
        return r.status_code, r.json()

    def unsubscribe(self,email):
        return self.change_subscription_status(email,status='unsubscribed')

    def subscribe(self,email):
        status_code, response_data = self.change_subscription_status(email,status='subscribed')
        # here in the videos it was shown that it just happens by using put command
        # but when the user email was not registered with mailchimp then it has to done using add email
        # when it is not there then status code will be 400 so its not 200 so we add the email
        if (status_code != 200):
            # print("status_code was not 200 ")
            status_code, response_data = self.add_email(email)
        # print("status, reponse: ", status_code, response_data)
        return status_code, response_data

    def pending(self,email):
        return self.change_subscription_status(email,status='pending')


from django.db import models

# Create your models here.
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .signals import object_viewed_signal
from .utils import get_client_ip

from django.contrib.sessions.models import Session
from django.db.models.signals import pre_save, post_save
from accounts.signals import user_logged_in

User = settings.AUTH_USER_MODEL

# below 2 things are looking in settings module for the 2nd args and default find value is taken as false
FORCE_SESSION_TO_ONE = getattr(settings,'FORCE_SESSION_TO_ONE', False)
FORCE_INACTIVE_USER_ENDSESSION = getattr(settings, 'FORCE_INACTIVE_USER_ENDSESSION', False)

# this class and receiver functions are to get the products viewed by the user on the website
class ObjectViewed(models.Model):
    user                = models.ForeignKey(User, blank= True, null=True, on_delete=models.CASCADE)  # user instance instance.id
    ip_address          = models.CharField(max_length=120, blank=True, null=True) # will be modified later on #IP FIELD
    content_type        = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # product, order, cart , address
    object_id           = models.PositiveIntegerField()    # user id , product id, order id
    content_object      = GenericForeignKey('content_type','object_id') # product instance
    timestamp           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s viewed on %s" %(self.content_object, self.timestamp)

    class Meta:
        ordering = ['-timestamp']  # most recent saved show up first
        verbose_name = 'Object viewed'
        verbose_name_plural = 'Objects viewed'

def object_viewed_receiver(sender, instance, request, *args, **kwargs):
    c_type  = ContentType.objects.get_for_model(sender) #sender is the instance.__class__
    #print(sender)
    #print(instance)
    #print(request)
    #print(request.user)
    user = None
    if request.user.is_authenticated:
        user = request.user
    new_view_obj = ObjectViewed.objects.create(
            user = user,
            object_id  = instance.id,
            content_type = c_type,
        # advantages of collecting the ip addresses is we can parse it and get the location of users and show the content
        # based on location but its not accurate Do put it on the website that we collect ip address of the user who
        # visits the website
        # if we are worried more about security then we should not collect this
            ip_address = get_client_ip(request)
        )

# notice that we dont have sender here because already we are sending the sender with the actual signal itself
# check analytics/mixins.py for reference
object_viewed_signal.connect(object_viewed_receiver )


#this is to get the session of the user when he is logged in
class UserSession(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)  # user instance instance.id
    ip_address = models.CharField(max_length=120, blank=True, null=True)  # will be modified later on #IP FIELD
    session_key = models.CharField(max_length=100, blank=True, null=True) # minimum length to be 50
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)  # we want to check whether or not this is an ended session
    ended = models.BooleanField(default=False)

    # function to delete the session when not used
    def end_session(self):
        session_key = self.session_key
        ended = self.ended
        try:
            Session.objects.get(pk= session_key).delete()
            self.active = False
            self.ended = True
            self.save()
        except:
            pass
        return self.ended

# we are ending the session for all except the current running one
def post_save_session_receiver(sender, instance, created, *args, **kwargs):
    if created:
        # to get all the sessions except the current session
        #qs = UserSession.objects.filter(user=instance.user).exclude(id = instance.id)
        # to allow multiple sessions of the user but only 1 active
        qs = UserSession.objects.filter(user = instance.user, ended = False, active = False).exclude(id=instance.id)
        for var in qs:
            var.end_session()
        if not instance.active and not instance.ended:
            #print("Hello")
            instance.end_session()


if FORCE_SESSION_TO_ONE:
    post_save.connect(post_save_session_receiver,sender = UserSession)

# to end session of the user after other user logs in from same desktop or something
def post_save_user_changed_receiver(sender, instance, created, *args, **kwargs):
    if not created:
        if instance.active ==False :
            qs = UserSession.objects.filter(user = instance.user,ended =False,active = False)
            for i in qs:
                i.end_session()


if FORCE_INACTIVE_USER_ENDSESSION:
    post_save.connect(post_save_user_changed_receiver,sender=User)

def user_logged_in_receiver(sender, instance, request , *args, **kwargs):
    print(instance)
    user = instance
    ip_address = get_client_ip(request)
    session_key = request.session.session_key # its correct after django 1.11
    UserSession.objects.create(
            user = user,
            ip_address = ip_address,
            session_key = session_key
        )

user_logged_in.connect(user_logged_in_receiver)


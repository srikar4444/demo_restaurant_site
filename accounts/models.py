from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
    )

# do go to user link to understand the default user account in django and what all we are going to modify
# https://www.codingforentrepreneurs.com/blog/how-to-create-a-custom-django-user-model/
# Create your models here.
class GuestEmail(models.Model):
    email           = models.EmailField()
    active          = models.BooleanField(default=True)
    updated         = models.DateTimeField(auto_now_add=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


#there are some default attributes that django produces in migrations.py once this function is just declared
# check 0002_customuser.py in migrations for the default attributes it creates
#class CustomUser(AbstractBaseUser) :
#    pass


class UserManager(BaseUserManager):
    def create_user(self,email,full_name=None, password= None,is_active = True, is_staff = False, is_admin = False):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a password")
        #if not full_name:
        #    raise ValueError("Users must have a full_name")
        user_obj = self.model(
            email = self.normalize_email(email),
            full_name = full_name

        )
        #this is how we set password
        user_obj.set_password(password)
        user_obj.active = is_active
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        # this line is django line for saving user content
        user_obj.save(using = self._db)
        return user_obj


    def create_staffuser(self, email,full_name=None,password = None):
        user = self.create_user(email, full_name, password= password,is_staff= True)
        return user

    def create_superuser(self,email,full_name=None, password = None):
        user = self.create_user(email, full_name, password= password,is_staff= True,is_admin=True)
        return user


# this is going to be our customUser class that is going to replace django's default user class so we are going to
# name it User eventhough django has a default User class
#class User(AbstractBaseUser,PermissionsMixin):
class User(AbstractBaseUser):
    email = models.EmailField(unique=True,max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null= True)
    active = models.BooleanField(default=True) # can login
    staff   = models.BooleanField(default=False) # staff user not superuser
    admin   = models.BooleanField(default=False) # superuser
    timestamp = models.DateTimeField(auto_now_add=True)
    #confirm = models.BooleanField(default=False)
    #confirmed_Date = models.DateTimeField()


    USERNAME_FIELD = 'email' # username this tells that the username which was unique previously will be the email field
    # email and password are required by default
    REQUIRED_FIELDS = []  #['full_name'] #python manage.py createsuperuser

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.email

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

    @property
    def is_superuser(self):
        return self.admin

    def has_perm(self,perm,obj=None):
        # does the user have a specific permission
        return self.admin

    def has_module_perms(self,app_label):
        #does the user have permissions to view app_label
        return self.admin

    @is_staff.setter
    def is_staff(self,value):
        self.is_staff = value


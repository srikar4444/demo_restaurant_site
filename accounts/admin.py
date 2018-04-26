from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm
# Register your models here.
from .models import GuestEmail

# https://www.codingforentrepreneurs.com/blog/how-to-create-a-custom-django-user-model/
# UserAdmin class is taken from above link

User = get_user_model()

"""
# this class is for searching the admin Model
class UserAdmin(admin.ModelAdmin):
    search_fields = ['email']

    form = UserAdminChangeForm # update view
    add_form = UserAdminCreationForm  # create view
    #class Meta:
    #    model = User
    
admin.site.register(User, UserAdmin )
"""

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'admin')
    list_filter = ('admin', 'staff', 'active',)  # somethings modified
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),  # in case of 'Personal info ' we can put 'Full name'
        ('Permissions', {'fields': ('admin','staff', 'active',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email','full_name' ,)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)

class GuestEmailAdmin(admin.ModelAdmin):
    search_fields = ['email']
    class Meta:
        model = GuestEmail

admin.site.register(GuestEmail, GuestEmailAdmin)
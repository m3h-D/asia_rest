from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.


class UserAdmin(BaseUserAdmin):
    """The forms to add and change user instances
    
    Arguments:
        BaseUserAdmin {MODULE} -- a built-in django Admin
    """
    # form = UserChangeForm
    # add_form = RegisterForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('phoneNo', 'get_full_name', 'email', 'id')
    # list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'phoneNo', 'password', 'username')}),
        ('Personal info', {'fields': (('first_name', 'last_name'),)}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_staff', 'user_permissions')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phoneNo', 'password')}
         ),
    )
    search_fields = ('phoneNo', 'first_name', 'last_name', 'email', 'id')

admin.site.register(User, UserAdmin)
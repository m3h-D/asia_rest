from django.contrib.auth import get_user_model, backends
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.conf import settings
from user.models import User as UserModel
from rest_framework import authentication
from rest_framework import exceptions

# UserModel = get_user_model()


class EmailBackend(backends.ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username))
        except UserModel.DoesNotExist:
            UserModel().set_password(password)

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        return super().authenticate(request, username, password, **kwargs)


class EmailAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = request.META.get('X_USERNAME') # get the username request header
        if not username: # no username passed in request headers
            return None # authentication did not succeed

        try:
            user = UserModel.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)) # get the user
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user') # raise exception if user does not exist 

        return (user, None) # authentication successful
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    address = models.CharField(_("Address"), max_length=255, blank=True, null=True)
    post_code = models.IntegerField(_("Post Code"), blank=True, null=True)
    phone_validator = RegexValidator(regex=r"[0][9][0-9]{9,9}$") # mobile validator
    phoneNo = models.CharField(max_length=11, validators=[phone_validator], blank=True, null=True)
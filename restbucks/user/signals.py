from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

@receiver(post_save, sender=User)
def create_auth_token(sender, instance, *args, **kwargs):
    """generate new token for every new account

    Args:
        sender (MODEL): a signal from user model after creation of record(register)
        instance (OBJECT): an object of user model
    """    
    if kwargs["created"]:   
        Token.objects.create(user=instance)


@receiver(pre_save, sender=User)
def generate_username(sender, instance, *args, **kwargs):
    """generates username for users that has no username assigned to
       them.

    Args:
        sender (MODEL): a signal from user model after save method call
        instance (OBJECT): an object of user model
    """    
    if instance.username is None or instance.username == "":
        email = instance.email.split("@")[0]
        try:
            instance.username = email
        except:
            instance.username = f"{email}__{instance.id}"

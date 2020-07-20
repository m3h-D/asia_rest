from celery import shared_task
from django.core.mail import EmailMessage


@shared_task
def send_email(to, status):
    msg = EmailMessage("Your Product Status", str(status), to=[str(to),])
    msg.send()

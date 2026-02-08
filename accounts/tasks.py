
from django.core.mail import EmailMultiAlternatives

def send_email(subject, body, to_email):
    email = EmailMultiAlternatives(
        subject,
        body,
        to=[to_email]
    )
    email.attach_alternative(body, "text/html")
    email.send()
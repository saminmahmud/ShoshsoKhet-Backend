from django.conf import settings
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature

signer = TimestampSigner()

def generate_email_token(user):
    return signer.sign(user.email)

def verify_email_token(token, max_age=60*60*24):  # 1 day expiration
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except SignatureExpired:
        return None
    except BadSignature:
        return None
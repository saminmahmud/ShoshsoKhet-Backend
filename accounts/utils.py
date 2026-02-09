from django.conf import settings
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.utils import timezone
from django.core.cache import cache
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

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
    


def cleanup_expired_tokens():
    # if cleanup already done recently, skip
    if cache.get("jwt_cleanup_lock"):
        return

    try:
        OutstandingToken.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
    except Exception:
        pass

    # lock for 1 hour
    cache.set("jwt_cleanup_lock", True, 60 * 60)
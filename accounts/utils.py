from django.conf import settings
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.utils import timezone
from django.core.cache import cache
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
import cloudinary.uploader
import os


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


# Cloudinary Image Handling
def delete_cloudinary_file(file_name):
    try:
        public_id = os.path.splitext(file_name)[0]
        cloudinary.uploader.destroy(public_id)
        # print(f"Cloudinary Deleted: {public_id}")
    except Exception as e:
        print(f"Cloudinary Delete Failed: {e}")


def delete_old_image_if_changed(instance, old_instance, field_name):
    """Delete old Cloudinary images if replaced or removed."""
    old_file = getattr(old_instance, field_name)
    new_file = getattr(instance, field_name)

    if old_file and old_file.name and (not new_file or old_file.name != new_file.name):
        delete_cloudinary_file(old_file.name)


def delete_all_images_on_delete(instance, field_name):
    """Delete all Cloudinary images when object deleted."""
    file_field = getattr(instance, field_name)
    if file_field and file_field.name:
        delete_cloudinary_file(file_field.name)
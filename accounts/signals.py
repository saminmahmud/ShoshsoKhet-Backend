from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from accounts.models import SellerProfile
from accounts.utils import delete_all_images_on_delete, delete_old_image_if_changed
from order.models import SellerWallet

User = get_user_model()

# Username generate from email before saving User instance
@receiver(pre_save, sender=User)
def set_username_from_email(sender, instance, **kwargs):
    if not instance.username and instance.email:
        base_username = instance.email.split('@')[0]
        username = slugify(base_username)

        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{slugify(base_username)}{counter}"
            counter += 1

        instance.username = username

@receiver(post_save, sender=SellerProfile)
def create_seller_wallet(sender, instance, created, **kwargs):
    if created:
        SellerWallet.objects.create(seller=instance)


# Cloudinary Image Handling
@receiver(pre_save, sender=User)
# Delete old profile image if changed
def auto_delete_old_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # Skip if new object

    try:
        old_instance = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    delete_old_image_if_changed(instance, old_instance, "profile_image")


@receiver(post_delete, sender=User)
# Delete profile image from Cloudinary when User deleted
def auto_delete_image_on_delete(sender, instance, **kwargs):
    delete_all_images_on_delete(instance, "profile_image")
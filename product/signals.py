# Cloudinary Image Handling
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import ProductImage
from accounts.utils import delete_all_images_on_delete, delete_cloudinary_file, delete_old_image_if_changed


@receiver(pre_save, sender=ProductImage)
def auto_delete_old_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # New image, no old image to delete
    
    try:
        old_instance = ProductImage.objects.get(pk=instance.pk)
    except ProductImage.DoesNotExist:
        return  # Old instance doesn't exist, nothing to delete
    delete_old_image_if_changed(old_instance, instance, 'image')



@receiver(post_delete, sender=ProductImage)
def auto_delete_image_on_delete(sender, instance, **kwargs):
    delete_all_images_on_delete(instance, 'image')
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Order

# hold previous order status
@receiver(pre_save, sender=Order)
def hold_previous_status(sender, instance, **kwargs):
    if instance.pk:
        previous = Order.objects.get(pk=instance.pk)
        instance._previous_status = previous.status
    else:
        instance._previous_status = None

@receiver(post_save, sender=Order)
def handle_stock_on_status_change(sender, instance, created, **kwargs):
    if created:
        return

    previous  = getattr(instance, '_previous_status', None)
    current  = instance.status

    # pending → confirmed
    if previous != 'confirmed' and current == 'confirmed':
        with transaction.atomic():
            for item in instance.items.select_related('product'):
                item.product.reduce_stock(item.quantity)

    # confirmed → cancelled
    if previous == 'confirmed' and current == 'cancelled':
        with transaction.atomic():
            for item in instance.items.select_related('product'):
                item.product.increase_stock(item.quantity)


@receiver(post_save, sender=Order)
def handle_platform_revenue_on_status_change(sender, instance, created, **kwargs):
    if created:
        return

    previous  = getattr(instance, '_previous_status', None)
    current  = instance.status

    # Order Delivered → Create Revenue 
    if previous != 'delivered' and current == 'delivered':
        instance.create_platform_revenue()

    # Order Cancelled after Delivered → Reverse Revenue 
    if previous == 'delivered' and current == 'cancelled':
        instance.reverse_platform_revenue()

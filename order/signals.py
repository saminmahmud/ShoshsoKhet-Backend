from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Order

# Hold previous order status
@receiver(pre_save, sender=Order)
def hold_previous_status(sender, instance, **kwargs):
    if instance.pk:
        previous = Order.objects.get(pk=instance.pk)
        instance._previous_status = previous.status
        instance._previous_is_paid = previous.is_paid
    else:
        instance._previous_status = None
        instance._previous_is_paid = False


@receiver(post_save, sender=Order)
def handle_payment_received(sender, instance, created, **kwargs):
    """
    When payment is successful (is_paid becomes True)
    Hold payment in escrow account
    """
    if created:
        return
    
    previous_is_paid = getattr(instance, '_previous_is_paid', False)
    current_is_paid = instance.is_paid
    
    # Payment just received
    if not previous_is_paid and current_is_paid:
        with transaction.atomic():
            # Hold payment in escrow
            success = instance.hold_payment_in_escrow()
            
            # if success:
            #     print(f"Payment held in escrow for order {instance.order_id}")
            # else:
            #     print(f"Failed to hold payment in escrow for order {instance.order_id}")



@receiver(post_save, sender=Order)
def handle_stock_on_status_change(sender, instance, created, **kwargs):
    if created:
        return

    previous = getattr(instance, '_previous_status', None)
    current = instance.status

    # pending → confirmed: Reduce stock
    if previous != 'confirmed' and current == 'confirmed':
        with transaction.atomic():
            for item in instance.items.select_related('product'):
                item.product.reduce_stock(item.quantity)
            
            # print(f"Stock reduced for order {instance.order_id}")

    # confirmed → cancelled: Restore stock
    if previous == 'confirmed' and current == 'cancelled':
        with transaction.atomic():
            for item in instance.items.select_related('product'):
                item.product.increase_stock(item.quantity)
            
            # print(f"Stock restored for order {instance.order_id}")



@receiver(post_save, sender=Order)
def handle_payment_release_on_delivery(sender, instance, created, **kwargs):
    """
    When order status changes to 'delivered'
    Release payment from escrow to seller wallets
    """
    if created:
        return

    previous = getattr(instance, '_previous_status', None)
    current = instance.status

    # Order just delivered → Release payment
    if previous != 'delivered' and current == 'delivered':
        with transaction.atomic():
            if not instance.delivered_at:
                from django.utils import timezone
                instance.delivered_at = timezone.now()
                Order.objects.filter(pk=instance.pk).update(delivered_at=instance.delivered_at)
            
            # Release payment to sellers
            success = instance.release_payment_to_sellers()
            
            if success:
                # Create platform revenue record
                instance.create_platform_revenue()
                # print(f"Payment released to sellers for order {instance.order_id}")
            # else:
                # print(f"Failed to release payment for order {instance.order_id}")


@receiver(post_save, sender=Order)
def handle_refund_on_cancellation(sender, instance, created, **kwargs):
    """
    When order is cancelled
    Refund payment to buyer if it was held in escrow
    """
    if created:
        return

    previous = getattr(instance, '_previous_status', None)
    current = instance.status

    # Order cancelled (but NOT from delivered state)
    if current == 'cancelled' and previous != 'delivered':
        with transaction.atomic():
            if instance.escrow_status == 'held':
                success = instance.refund_to_buyer(
                    reason=f"Order cancelled - Status changed from {previous} to cancelled"
                )
                
                # if success:
                #     print(f"Payment refunded to buyer for order {instance.order_id}")
                # else:
                #     print(f"Failed to refund payment for order {instance.order_id}")

    # Order cancelled AFTER delivery → Reverse revenue
    if previous == 'delivered' and current == 'cancelled':
        with transaction.atomic():
            instance.reverse_platform_revenue()
            # print(f"Revenue reversed for cancelled order {instance.order_id}")
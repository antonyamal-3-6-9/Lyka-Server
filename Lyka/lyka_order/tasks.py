from .models import Order
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from lyka_payment.models import OrderTransaction
from lyka_user.models import Notification
from lyka_products.models import Unit
import string
import random
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_order_update_notification(user_id, message, time):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'send_order_update',
            'message': message,
            'time': time
        }
    )

def generate_transaction_ref_no(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))

    timestamp_ms = int(time.time() * 1000)

    return f"TXN-{timestamp_ms}-{random_string}"

def generate_transaction(order):
    transaction_ref_no = generate_transaction_ref_no(13)

    OrderTransaction.objects.create(
        payer=order.customer,
        payee=order.seller,
        order=order,
        entry=order.payment_method,
        amount=order.item.product_price,
        ref_no=transaction_ref_no,
        is_successful=True,
        profit=order.item.product_price - order.item.original_price,
        quantity=order.item.quantity,
        notes=f'Transaction recorded for the Order of {order.item.product.brand} {order.item.product.name} {order.item.product_variant} {order.item.product_color} from {order.seller.bussiness_name} to {order.shipping_address.name}'
    )

def update_transaction(order):
    transaction = OrderTransaction.objects.get(order=order, payee=order.seller, payer=order.customer, is_successful=True)
    transaction.is_successful = False
    transaction.save()

def change_order_status(order, new_status):
    order.status = new_status
    order.time = timezone.now()
    order.save()

def notify_order_update(order, new_status):
    message = f'Your order {order.item.product.brand} {order.item.product.name} of {order.order_id} has been {new_status}'
    notification_c = Notification.objects.create(owner=order.customer.user, message=message)
    notification_s = Notification.objects.create(owner=order.seller.user, message=message)
    send_order_update_notification(order.customer.user.id, notification_c.message, time=str(notification_c.time))
    send_order_update_notification(order.seller.user.id, notification_s.message, time=str(notification_s.time))

@shared_task
def updating_order():
    print("doing")
    order_status_updates = [
        (Order.CONFIRMED, Order.PICKED_UP, 2),
        (Order.PICKED_UP, Order.SHIPPED, 2),
        (Order.SHIPPED, Order.IN_TRANSIST, 2),
        (Order.IN_TRANSIST, Order.OUT_OF_DELIVERY, 2),
        (Order.CANCELATION_REQUESTED, Order.CANCELLED, 2),
        (Order.OUT_OF_DELIVERY, Order.DELIVERED, 2),
        (Order.RETURN_REQUESTED, Order.RETURN_IN_TRANSIST, 2),
        (Order.RETURN_IN_TRANSIST, Order.RETURNED, 2),
    ]

    current_time = timezone.now()

    for from_status, to_status, minutes in order_status_updates:
        orders = Order.objects.filter(status=from_status, time__lte=current_time - timezone.timedelta(minutes=minutes))

        for order in orders:
            change_order_status(order, to_status)
            notify_order_update(order, to_status)

            if to_status == Order.DELIVERED:
                unit = Unit.objects.get(
                    variant=order.item.product_variant,
                    color_code=order.item.product_color,
                    product=order.item.product,
                    seller=order.seller
                )
                unit.units_sold += order.item.quantity
                unit.save()

                if generate_transaction(order=order):
                    notify_order_update(order, to_status)
                elif to_status == Order.RETURNED:
                    update_transaction(order)
                    notify_order_update(order, to_status)

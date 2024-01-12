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
            'time' : time
        }
    )

# @shared_task
# def printingTask():
#     send_order_update_notification(user_id=11, message="Celery is working")


def generate_transaction_ref_no(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))

    timestamp_ms = int(time.time() * 1000)

    transaction_ref_no = f"TXN-{timestamp_ms}-{random_string}"
    return transaction_ref_no


def generate_transaction(order):
    transaction = OrderTransaction.objects.create(
                payer = order.customer,
                payee = order.seller,
                order = order,
                entry = order.payment_method,
                amount = order.item.product_price,
                ref_no = generate_transaction_ref_no(13),
                is_successful = True,
                profit = order.item.product_price - order.item.original_price,
                quantity = order.item.quantity,
                notes = f'Transaction recorded for the Return of Order {order.item.product.brand} {order.item.product.name} {order.item.product_variant} {order.item.product_color} from {order.seller.bussiness_name} to {order.shipping_address.name}'
            )
    return True


def update_transaction(order):
    transaction = OrderTransaction.objects.get(order=order, payee=order.seller, payer=order.customer, is_successful=True)
    transaction.is_successful = False
    transaction.save()
    return True


@shared_task
def updating_order():
    print("doing")
    accepted_orders = Order.objects.filter(status=Order.CONFIRMED)
    pickedup_orders = Order.objects.filter(status=Order.PICKED_UP)
    in_transit_orders = Order.objects.filter(status=Order.IN_TRANSIST)
    shipped_orders = Order.objects.filter(status=Order.SHIPPED)
    out_of_delivery_orders = Order.objects.filter(status=Order.OUT_OF_DELIVERY)
    return_requested_orders = Order.objects.filter(status=Order.RETURN_REQUESTED)
    return_picked_up_orders = Order.objects.filter(status=Order.RETURN_IN_TRANSIST)
    cancellation_requested_orders = Order.objects.filter(status=Order.CANCELATION_REQUESTED)
    current_time = timezone.now()  

    for order in accepted_orders:
        order_time_naive = order.time
        pick_up_time = order_time_naive + timedelta(minutes=2)
        print(order.time.tzinfo)

        if current_time > pick_up_time:
            order.status = Order.PICKED_UP
            order.time = current_time
            order.save()
            message = f'Your order {order.item.product.brand} {order.item.product.name} of {order.order_id} has been {order.status}'
            notification_c = Notification.objects.create(owner=order.customer.user, message=message)
            notification_s = Notification.objects.create(owner=order.seller.user, message=message)
            send_order_update_notification(order.customer.user.id, notification_c.message, time=str(notification_c.time))
            send_order_update_notification(order.seller.user.id, notification_s.message, time=str(notification_s.time))


    for order in pickedup_orders:
        order_time_naive = order.time
        transist_time = order_time_naive + timedelta(minutes=2)

        if current_time > transist_time:
            order.status = order.SHIPPED 
            order.time = current_time
            order.save()
            message = f'Your order {order.item.product.brand} {order.item.product.name} of {order.order_id} has been {order.status}'
            notification_c = Notification.objects.create(owner=order.customer.user, message=message)
            notification_s = Notification.objects.create(owner=order.seller.user, message=message)
            send_order_update_notification(order.customer.user.id, notification_c.message, time=str(notification_c.time))
            send_order_update_notification(order.seller.user.id, notification_s.message, time=str(notification_s.time))

    for order in shipped_orders:
        order_time_naive = order.time
        shipping_time = order_time_naive + timedelta(minutes=2)

        if current_time > shipping_time:
            order.status = Order.IN_TRANSIST 
            order.time = current_time
            order.save()
            message = f'Your order {order.item.product.brand} {order.item.product.name} of {order.order_id} has been {order.status}'
            notification_c = Notification.objects.create(owner=order.customer.user, message=message)
            notification_s = Notification.objects.create(owner=order.seller.user, message=message)
            send_order_update_notification(order.customer.user.id, notification_c.message, time=str(notification_c.time))
            send_order_update_notification(order.seller.user.id, notification_s.message, time=str(notification_s.time))

    for order in in_transit_orders:
        order_time_naive = order.time
        out_of_delivery_time = order_time_naive + timedelta(minutes=2)

        if current_time > out_of_delivery_time:
            order.status = Order.OUT_OF_DELIVERY
            order.time = current_time
            order.save()
            if generate_transaction(order=order):
                message = f'Your order {order.item.product.brand} {order.item.product.name} of {order.order_id} has been {order.status}'
                notification_c = Notification.objects.create(owner=order.customer.user, message=message)
                notification_s = Notification.objects.create(owner=order.seller.user, message=message)
                send_order_update_notification(order.customer.user.id, notification_c.message, time=str(notification_c.time))
                send_order_update_notification(order.seller.user.id, notification_s.message, time=str(notification_s.time))

    
    for order in cancellation_requested_orders:
        order_time_naive = order.time
        cancel_time = order_time_naive + timedelta(minutes=2)

        if current_time > cancel_time:
            order.status = Order.CANCELLED
            order.time = current_time
            order.save()
            if generate_transaction(order=order):
                message = f'Your order {order.item.product.brand} {order.item.product.name} of {order.order_id} has been {order.status}'
                notification_c = Notification.objects.create(owner=order.customer.user, message=message)
                notification_s = Notification.objects.create(owner=order.seller.user, message=message)
                send_order_update_notification(order.customer.user.id, notification_c.message, time=str(notification_c.time))
                send_order_update_notification(order.seller.user.id, notification_s.message, time=str(notification_s.time))

        for order in out_of_delivery_orders:
            order_time_naive = order.time
            delivery_time = order_time_naive + timedelta(minutes=2)

            if current_time > delivery_time:
                order.status = Order.DELIVERED
                order.time = current_time
                order.save()
                unit = Unit.objects.get(variant=order.item.product_variant,
                                color_code=order.item.product_color, product=order.item.product, seller=order.seller)
                old_sale = unit.units_sold
                new_sale = int(old_sale) + int(order.item.quantity)
                unit.units_sold = new_sale
                unit.save()
                if generate_transaction(order=order):
                    message = f'Your order {order.item.product.brand} {order.item.product.name} of {order.order_id} has been {order.status}'
                    notification_c = Notification.objects.create(owner=order.customer.user, message=message)
                    notification_s = Notification.objects.create(owner=order.seller.user, message=message)
                    send_order_update_notification(order.customer.user.id, notification_c.message, time=str(notification_c.time))
                    send_order_update_notification(order.seller.user.id, notification_s.message, time=str(notification_s.time))

    for order in return_requested_orders:
        order_time_naive = order.time
        requested_time = order_time_naive + timedelta(minutes=2)

        if current_time > requested_time:
            order.status = Order.RETURN_IN_TRANSIST 
            order.time = current_time
            order.save()
            message = f'Your order {order.item.product.brand} {order.item.product.name} of {order.order_id} has been {order.status}'
            notification_c = Notification.objects.create(owner=order.customer.user, message=message)
            notification_s = Notification.objects.create(owner=order.seller.user, message=message)
            send_order_update_notification(order.customer.user.id, notification_c.message, time=str(notification_c.time))
            send_order_update_notification(order.seller.user.id, notification_s.message, time=str(notification_s.time))


    for order in return_picked_up_orders:
        order_time_naive = order.time
        pick_up_time = order_time_naive + timedelta(minutes=2)

        if current_time > pick_up_time:
            order.status = Order.RETURNED
            order.time = current_time
            order.save()
            unit = Unit.objects.get(variant=order.item.product_variant,
                                color_code=order.item.product_color, product=order.item.product, seller=order.seller)
            old_sale = unit.units_sold
            old_stock = unit.stock
            new_sale = int(old_sale) - int(order.item.quantity)
            new_stock = int(old_stock) + int(order.item.quantity)
            unit.stock = new_stock
            unit.units_sold = new_sale
            unit.save()
            if update_transaction(order):
                message = f'Your order {order.item.product.brand} {order.item.product.name} of {order.order_id} has been {order.status}'
                notification_c = Notification.objects.create(owner=order.customer.user, message=message)
                notification_s = Notification.objects.create(owner=order.seller.user, message=message)
                send_order_update_notification(order.customer.user.id, notification_c.message, time=str(notification_c.time))
                send_order_update_notification(order.seller.user.id, notification_s.message, time=str(notification_s.time))


from .models import Order
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from lyka_payment.models import OrderTransaction
import string
import random
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_order_update_notification(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'send_order_update',
            'message': message,
            'user_id' : user_id
        }
    )



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
def printingTask():
    print("hy")
    send_order_update_notification(11, "hy Da")

@shared_task
def updating_order():
    accepted_orders = Order.objects.filter(order_status="Accepted")
    pickedup_orders = Order.objects.filter(order_status="Picked Up")
    in_transit_orders = Order.objects.filter(order_status="In Transit")
    shipped_orders = Order.objects.filter(order_status="Shipped")
    return_requested_orders = Order.objects.filter(order_status="Return Requested")
    return_picked_up_orders = Order.objects.filter(order_status="Picked Up for Return")
    current_time = timezone.now()  

    for order in accepted_orders:
        order_time_naive = order.time
        pick_up_time = order_time_naive + timedelta(minutes=15)
        print(order.time.tzinfo)

        if current_time > pick_up_time:
            order.order_status = "Picked Up"
            order.time = current_time
            order.save()
            message = f'Your order {order.order_id} has been Picked up'
            print(message)
            send_order_update_notification(order.customer.user.id, message)
            send_order_update_notification(order.seller.user.id, message)


    for order in pickedup_orders:
        order_time_naive = order.time
        transist_time = order_time_naive + timedelta(minutes=15)

        if current_time > transist_time:
            order.order_status = "In Transit"
            order.time = current_time
            order.save()
            message = f'Your order {order.order_id} id In Transist'
            print(message)
            send_order_update_notification(order.customer.user.id, message)
            send_order_update_notification(order.seller.user.id, message)


    for order in in_transit_orders:
        print("hy order")
        order_time_naive = order.time
        shipping_time = order_time_naive + timedelta(minutes=15)

        if current_time > shipping_time:
            order.order_status = "Shipped"
            order.time = current_time
            order.save()
            message = f'Your order {order.order_id} has been shipped'
            print(message)
            send_order_update_notification(order.customer.user.id, message)
            send_order_update_notification(order.seller.user.id, message)

    for order in shipped_orders:
        order_time_naive = order.time
        delivery_time = order_time_naive + timedelta(minutes=15)

        if current_time > delivery_time:
            order.order_status = "Delivered"
            order.time = current_time
            order.save()
            if generate_transaction(order=order):
                message = f'Your order {order.order_id} has been shipped'
                print(message)
                send_order_update_notification(order.customer.user.id, message)
                send_order_update_notification(order.seller.user.id, message)


    for order in return_requested_orders:
        order_time_naive = order.time
        requested_time = order_time_naive + timedelta(minutes=15)

        if current_time > requested_time:
            order.order_status = "Picked Up for Return"
            order.time = current_time
            order.save()
            message = f'Your order {order.order_id} has been Picked up for return'
            print(message)
            send_order_update_notification(order.customer.user.id, message)
            send_order_update_notification(order.seller.user.id, message)


    for order in return_picked_up_orders:
        order_time_naive = order.time
        pick_up_time = order_time_naive + timedelta(minutes=30)

        if current_time > pick_up_time:
            order.order_status = "Returned"
            order.time = current_time
            order.save()
            if update_transaction(order):
                message = f'Your order {order.order_id} has been Returned Successfully'
                print(message)
                send_order_update_notification(order.customer.user.id, message)
                send_order_update_notification(order.seller.user.id, message)


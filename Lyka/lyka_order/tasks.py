from .models import Order
from datetime import timedelta, datetime
from django.utils import timezone
from celery import shared_task
from lyka_payment.models import OrderTransaction
import string
import random
import time



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
                notes = f'Transaction recorded for the order of {order.item.product.brand} {order.item.product.name} {order.item.product_variant} {order.item.product_color} from {order.seller.bussiness_name} to {order.shipping_address.name}'
            )
    return True


def update_transaction(order):
    transaction = OrderTransaction.objects.get(order=order, payee=order.seller, payer=order.customer, is_successful=True)
    transaction.is_successful = False
    transaction.save()
    return True

@shared_task
def updating_order():
    accepted_orders = Order.objects.filter(order_status="Accepted")
    pickedup_orders = Order.objects.filter(order_status="Picked Up")
    in_transit_orders = Order.objects.filter(order_status="In Transit")
    shipped_orders = Order.objects.filter(order_status="Shipped")
    return_requested_orders = Order.objects.filter(order_status="Return Requested")
    return_picked_up_orders = Order.objects.filter(order_status="Picked Up for Return")
    current_time = datetime.now()  
    print("running")

    for order in accepted_orders:
        order_time_naive = order.time.astimezone(timezone.utc).replace(tzinfo=None) 
        pick_up_time = order_time_naive + timedelta(minutes=15)


        if current_time > pick_up_time:
            order.order_status = "Picked Up"
            order.time = current_time
            order.save()
            print(f'{order.order_id} has been Picked up')

    for order in pickedup_orders:
        order_time_naive = order.time.astimezone(timezone.utc).replace(tzinfo=None) 
        transist_time = order_time_naive + timedelta(minutes=15)

        if current_time > transist_time:
            order.order_status = "In Transit"
            order.time = current_time
            order.save()
            print(f'{order.order_id} has been In Transit')

    for order in in_transit_orders:
        order_time_naive = order.time.astimezone(timezone.utc).replace(tzinfo=None) 
        shipping_time = order_time_naive + timedelta(minutes=15)

        if current_time > shipping_time:
            order.order_status = "Shipped"
            order.time = current_time
            order.save()
            print(f'{order.order_id} has been Shipped')

    for order in shipped_orders:
        order_time_naive = order.time.astimezone(timezone.utc).replace(tzinfo=None) 
        delivery_time = order_time_naive + timedelta(minutes=15)

        if current_time > delivery_time:
            order.order_status = "Delivered"
            order.time = current_time
            order.save()
            if generate_transaction(order=order):
                print(f'{order.order_id} has been Delivered')


    for order in return_requested_orders:
        order_time_naive = order.time.astimezone(timezone.utc).replace(tzinfo=None) 
        requested_time = order_time_naive + timedelta(minutes=15)

        if current_time > requested_time:
            order.order_status = "Picked Up for Return"
            order.time = current_time
            order.save()
            print(f'{order.order_id} has been picked up for return')


    for order in return_picked_up_orders:
        order_time_naive = order.time.astimezone(timezone.utc).replace(tzinfo=None) 
        pick_up_time = order_time_naive + timedelta(minutes=30)

        if current_time > pick_up_time:
            order.order_status = "Returned"
            order.time = current_time
            order.save()
            if update_transaction(order):
                print(f'{order.order_id} has been returned successfully')


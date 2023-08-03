from .signals import order_placed
from django.dispatch import receiver

@receiver(order_placed)
def update_unit_stock(sender, **kwargs):
    unit = kwargs["unit"]
    quantity = kwargs["quantity"]
    old_stock = unit.stock
    new_stock = int(old_stock) - int(quantity)
    unit.stock = new_stock
    unit.save()
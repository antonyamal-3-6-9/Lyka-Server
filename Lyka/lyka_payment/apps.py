from django.apps import AppConfig




class LykaPaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lyka_payment'

    def ready(self):
        from . import signals
        from lyka_customer.models import Customer
        from .recievers import update_unit_stock
        signals.order_placed.connect(update_unit_stock, sender=Customer)
    

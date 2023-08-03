from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(CouponType)
admin.site.register(OrderTransaction)
admin.site.register(Wallet)
admin.site.register(SalesReport)

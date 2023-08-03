from django.db import models
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from lyka_order.models import Order

# Create your models here.

class Wallet(models.Model):
    wallet_id = models.UUIDField(primary_key=True)
    wallet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    currency = models.CharField(max_length=3, default="INR")
    last_transaction_date = models.DateTimeField(null=True, blank=True)
    transaction_limit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    transaction_count = models.PositiveIntegerField(default=0)

class OrderTransaction(models.Model):
    payer = models.ForeignKey('lyka_customer.Customer', on_delete=models.CASCADE)
    payee = models.ForeignKey('lyka_seller.Seller', on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    order = models.ForeignKey('lyka_order.Order', on_delete=models.CASCADE)
    entry = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    ref_no = models.UUIDField(primary_key=True)
    time = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=False)
    notes = models.TextField(blank=True)


class SalesReport(models.Model):
    seller = models.ForeignKey('lyka_seller.Seller', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    sales_by_customer = models.JSONField()

    def __str__(self):
        return f"Sales Report for {self.seller} ({self.start_date} - {self.end_date})"

 
def generate_report(seller, start_date, end_date):

    transactions = OrderTransaction.objects.filter(payee=seller, time__range=(start_date, end_date), is_successful=True)

    total_sales = transactions.aggregate(total_sales=Sum('amount'))['total_sales']

    sales_by_customer = transactions.values('payer').annotate(total_sales=Sum('amount'))


    sales_report = SalesReport(
        seller=seller,
        start_date=start_date,
        end_date=end_date,
        total_sales=total_sales,
        sales_by_customer=sales_by_customer
        )
    sales_report.save()

    return sales_report

class CouponType(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="The coupon code.")
    description = models.TextField(blank=True, null=True, help_text="Description of the coupon.")
    maximum_discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Discount percentage.")
    minimum_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Minimum purchase amount for the coupon to be valid.")
    max_usage_limit = models.PositiveIntegerField(default=1, help_text="Maximum number of times the coupon can be used.")
    start_date = models.DateTimeField(default=timezone.now, help_text="Start date and time of the coupon validity.")
    end_date = models.DateTimeField(help_text="End date and time of the coupon validity.")
    is_active = models.BooleanField(default=True, help_text="Whether the coupon is currently active.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the coupon was created.")

    def __str__(self):
        return self.code

class CouponUsage(models.Model):
    customer = models.ForeignKey('lyka_customer.Customer', on_delete=models.CASCADE)
    coupon_type = models.ForeignKey(CouponType, on_delete=models.CASCADE)
    usage_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.customer} - {self.coupon_type}"
    


    



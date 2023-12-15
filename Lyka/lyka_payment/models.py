from django.db import models
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from lyka_order.models import Order

# Create your models here.

class Wallet(models.Model):
    wallet_id = models.UUIDField(primary_key=True)
    wallet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    currency = models.CharField(max_length=3, default="INR")
    last_transaction_date = models.DateTimeField(null=True, blank=True)
    transaction_count = models.PositiveIntegerField(default=0)

class OrderTransaction(models.Model):
    payer = models.ForeignKey('lyka_customer.Customer', on_delete=models.CASCADE)
    payee = models.ForeignKey('lyka_seller.Seller', on_delete=models.CASCADE)
    order = models.ForeignKey('lyka_order.Order', on_delete=models.CASCADE)
    entry = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    ref_no = models.CharField(primary_key=True, max_length=100)
    time = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    date=models.DateField(null=True, db_index=True)    
    

class SalesReport(models.Model):
    seller = models.ForeignKey('lyka_seller.Seller', on_delete=models.CASCADE)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    total_sales = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    total_products_sold = models.PositiveIntegerField(default=0, null=True)
    total_amount_refunded = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_refunds = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Sales Report for {self.seller} ({self.start_date} - {self.end_date})"

 
def generate_report_timeline(seller, start_date, end_date):
    total_amount = 0
    total_profit = 0
    total_units_sold = 0
    total_sales = 0
    total_refund = 0
    total_amount_refunded = 0
    transactions = OrderTransaction.objects.filter(payee=seller, date__range=(start_date, end_date), is_successful=True)
    unsuccessful_transactions = OrderTransaction.objects.filter(payee=seller, date__range=(start_date, end_date), is_successful=False)
    if transactions:
        total_sales = len(transactions)
        total_units_sold = transactions.aggregate(total_units_sold=Sum('quantity'))["total_units_sold"]
        total_amount= transactions.aggregate(total_amount=Sum('amount'))['total_amount']
        total_profit = transactions.aggregate(total_profit=Sum('profit'))['total_profit']
    if unsuccessful_transactions:
        total_refund = len(unsuccessful_transactions)
        total_amount_refunded = unsuccessful_transactions.aggregate(total_amount_refunded=Sum('amount'))['total_amount_refunded']



    sales_report, created = SalesReport.objects.get_or_create(pk=1)
    
    sales_report.seller=seller,
    sales_report.start_date=start_date,
    sales_report.end_date=end_date,
    sales_report.total_sales=total_sales,
    sales_report.total_profit=total_profit,
    sales_report.total_amount=total_amount,
    sales_report.total_products_sold=total_units_sold,
    sales_report.total_refunds=total_refund,
    sales_report.total_amount_refunded=total_amount_refunded
        
    sales_report.save()
    return sales_report


def generate_report(seller):
    total_amount = 0
    total_profit = 0
    total_units_sold = 0
    total_sales = 0
    total_refund = 0
    total_amount_refunded = 0
    transactions = OrderTransaction.objects.filter(payee=seller, is_successful=True)
    unsuccessful_transactions = OrderTransaction.objects.filter(payee=seller,  is_successful=False)    
    if transactions:
        total_sales = len(transactions) + 1
        total_units_sold = transactions.aggregate(total_units_sold=Sum('quantity'))["total_units_sold"]
        total_amount= transactions.aggregate(total_amount=Sum('amount'))['total_amount']
        total_profit = transactions.aggregate(total_profit=Sum('profit'))['total_profit']
    if unsuccessful_transactions:
        total_refund = len(unsuccessful_transactions)
        total_amount_refunded = unsuccessful_transactions.aggregate(total_amount_refunded=Sum('amount'))['total_amount_refunded']

    sales_report, created = SalesReport.objects.get_or_create(pk=1)

    sales_report.seller=seller,
    sales_report.total_sales=total_sales,
    sales_report.total_profit=total_profit, 
    sales_report.total_products_sold=total_units_sold,
    sales_report.total_amount=total_amount,
    sales_report.total_refunds=total_refund,
    sales_report.total_amount_refunded=total_amount_refunded

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
    


    



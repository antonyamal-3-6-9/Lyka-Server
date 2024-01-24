from django.db import models
from django.utils import timezone
from django.db.models import Sum

# Create your models here.

class Commission(models.Model):
    amount = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0)
    date = models.DateField(default= timezone.now)
    is_successful = models.BooleanField(default=False)
    ref_no = models.CharField(unique=True, max_length=8)


class Total_Commission(models.Model):
    income = models.DecimalField(max_digits = 15, decimal_places = 2, default = 0)
    total_no = models.IntegerField(default=0)


    def calculate_total(start_date = None, end_date = None):
        commissions = None
        total_amount = 0

        if start_date is None and end_date is None:
            commissions = Commission.objects.filter(is_successful = True)
        else:
            commissions = Commission.objects.filter(date__range = (start_date, end_date),is_successful = True)

        total_commission, created = Total_Commission.objects.get_or_create(pk=1)
        
        if commissions:
            total_amount = commissions.aggregate(total_amount= Sum("amount"))[total_amount]
            total_commission.income = total_amount
            total_commission.total_no = len(commissions)
        total_commission.save()
        return total_commission
    


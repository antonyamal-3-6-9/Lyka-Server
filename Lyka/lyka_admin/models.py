from django.db import models
from django.utils import timezone

# Create your models here.

class Commission(models.Model):
    amount = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0)
    date = models.DateField(default= timezone.now)
    is_successful = models.BooleanField(default=False)


class Total_Commission(models.model):
    income = models.DecimalField(max_digits = 15, decimal_places = 2, default = 0)

    def calculate_total(start_date = None, end_date = None):

        commissions = None
        total_amount = 0

        if start_date is None and end_date is None:
            commissions = Commission.objects.filter(is_successful = True)
        else:
            commissions = Commission.objects.filter(date__range = (start_date, end_date),is_successful = True)

        total_amount = commissions.aggregate(total_amount= sum("amount"))[total_amount]
        total_commission = Total_Commission.objects.get_or_create(pk=1)
        total_commission.income = total_amount
        total_commission.save()

        return total_commission
    


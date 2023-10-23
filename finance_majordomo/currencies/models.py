from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class CurrencyRate(models.Model):

    tradedate = models.DateField()
    price_usd = models.DecimalField(max_digits=8, decimal_places=4, null=True)

    is_closed = models.BooleanField(blank=False)
    update_time = models.DateTimeField(blank=True, null=True)


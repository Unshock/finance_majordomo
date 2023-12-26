from django.db import models
from django.utils.translation import gettext_lazy as _


class CurrencyRate(models.Model):

    tradedate = models.DateField(verbose_name=_('The date of the rate data'))

    price_usd = models.DecimalField(
        max_digits=8, decimal_places=4, null=True,
        verbose_name=_('CBR usd rate for the date'))

    price_euro = models.DecimalField(
        max_digits=8, decimal_places=4, null=True,
        verbose_name=_('CBR usd rate for the date'))

    is_closed = models.BooleanField(
        blank=False,
        verbose_name=_('Shows if date is closed and can not be updated')
    )

    update_time = models.DateTimeField(
        blank=True, null=True, verbose_name=_('Last update time'))


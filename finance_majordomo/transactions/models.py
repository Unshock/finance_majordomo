from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock, Asset
from finance_majordomo.users.models import User, Portfolio


# Create your models here.
class Transaction(models.Model):

    transaction_type_choices = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        #('SELL', 'Sell'),
    ]

    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creation date')
    )

    transaction_type = models.CharField(
        max_length=4,
        choices=transaction_type_choices,
        verbose_name=_('Transaction type'),
        validators=[MinLengthValidator(1)]
    )

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        verbose_name=_('Transaction portfolio'),
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        verbose_name=_('Asset'),
    )

    date = models.DateField(
        max_length=10,
        verbose_name=_('Transaction date'),
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_('Transaction price'),
    )

    accrued_interest = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        default=Decimal('0'),
        verbose_name=_('Accrued Interest')
    )

    fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        default=Decimal('0'),
        verbose_name=_('Transaction fee')
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Transaction quantity'),
    )


    def get_delete_url(self):
        return reverse("delete_transaction", kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.transaction_type} ' \
               f'x{self.quantity} {self.asset.secid} ' \
               f'for {self.price} on {self.date}'

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ['creation_date', 'asset', 'portfolio']
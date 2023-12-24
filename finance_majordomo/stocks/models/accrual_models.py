from django.db import models
from django.utils.translation import gettext_lazy as _

from finance_majordomo.stocks.models.asset import Asset
from finance_majordomo.users.models import Portfolio


class Accrual(models.Model):

    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Creation date"))

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )

    date = models.DateField(
        verbose_name=_("Accrual date")
    )

    #make not null:
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Accrual amount for one asset"))

    portfolios = models.ManyToManyField(
        Portfolio,
        through='AccrualsOfPortfolio',
        through_fields=('accrual', 'portfolio'),
        blank=True,
        related_name='accrual',
    )

    class Meta:
        verbose_name = "Начисление"
        verbose_name_plural = "Начисления"
        ordering = ['creation_date', 'asset', 'amount']


class AccrualsOfPortfolio(models.Model):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        null=True
    )

    accrual = models.ForeignKey(
        Accrual,
        on_delete=models.CASCADE,
        null=True
    )

    is_received = models.BooleanField(
        default=False,
        help_text='shows if portfolio got accrual',
        verbose_name='Accrual status'
    )

    class Meta:

        unique_together = ('portfolio', 'accrual')
        verbose_name = "Начисление портфеля"
        verbose_name_plural = "Начисления портфеля"
        ordering = ['accrual']

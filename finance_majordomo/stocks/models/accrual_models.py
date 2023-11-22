from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models.asset import Stock, Asset
from finance_majordomo.users.models import User, Portfolio


class Dividend(models.Model):
    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Creation date"))

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )

    date = models.DateField(
        verbose_name=_("Dividend date")
    )

    #make not null:
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Dividend amount for one share"))

    users = models.ManyToManyField(
        User,
        through='DividendsOfUser',
        through_fields=('dividend', 'user'),
        blank=True,
        related_name='dividend',
    )


    class Meta:
        verbose_name = "Дивиденд"
        verbose_name_plural = "Дивиденды"
        ordering = ['creation_date', 'asset', 'amount']


class DividendsOfUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )

    dividend = models.ForeignKey(
        Dividend,
        on_delete=models.CASCADE,
        null=True
    )

    is_received = models.BooleanField(
        default=False,
        help_text='shows if user got dividend',
        verbose_name='Dividend status')

    class Meta:

        unique_together = ('user', 'dividend')
        verbose_name = "Дивиденд пользователя"
        verbose_name_plural = "Дивиденды пользователей"
        ordering = ['dividend']


class DividendsOfPortfolio(models.Model):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        null=True
    )

    dividend = models.ForeignKey(
        Dividend,
        on_delete=models.CASCADE,
        null=True
    )

    is_received = models.BooleanField(
        default=False,
        help_text='shows if portfolio got dividend',
        verbose_name='Dividend status')

    class Meta:

        unique_together = ('portfolio', 'dividend')
        verbose_name = "Дивиденд портфеля"
        verbose_name_plural = "Дивиденды портфеля"
        ordering = ['dividend']

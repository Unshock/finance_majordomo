from django.db import models
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

from finance_majordomo.users.models import Portfolio


class Asset(models.Model):

    asset_types = [
        ('stocks', 'stocks'),
        ('bonds', 'bonds'),
        ('currencies', 'currencies'),
        ('funds', 'funds')
    ]

    creation_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")

    asset_type = models.CharField(max_length=20,
                                  choices=asset_types,
                                  verbose_name='Тип актива')

    # ticker = models.CharField(
    #     max_length=10,
    #     verbose_name="Тикер акции",
    #     unique=True
    # )

    portfolios = models.ManyToManyField(
        Portfolio,
        through='AssetOfPortfolio',
        through_fields=('asset', 'portfolio'),
        #blank=True,
        related_name='asset',
    )


class AssetOfPortfolio(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Объекты портфеля"
        verbose_name_plural = "Объекты портфеля"
        ordering = ['portfolio']

from django.db import models
from django.urls import reverse

from django.utils.translation import gettext_lazy as _


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

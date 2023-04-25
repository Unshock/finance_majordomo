from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock


class Dividend(models.Model):
    creation_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE,
                              null=True)
    date = models.CharField(max_length=10, verbose_name='Дата дивиденда')
    dividend = models.DecimalField(max_digits=8, decimal_places=2,
                                   verbose_name='Размер дивиденда на акцию')


    class Meta:
        verbose_name = "Дивиденд"
        verbose_name_plural = "Дивиденды"
        ordering = ['creation_date', 'stock', 'dividend']

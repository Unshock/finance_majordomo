from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock
from finance_majordomo.users.models import User


class Dividend(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True,
                                         verbose_name="Дата создания")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Дата дивиденда')
    amount = models.DecimalField(max_digits=8, decimal_places=2,
                                 verbose_name='Размер дивиденда на акцию')

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
        ordering = ['creation_date', 'stock', 'amount']


class DividendsOfUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             null=True)
    dividend = models.ForeignKey(Dividend, on_delete=models.CASCADE,
                                 null=True)
    is_received = models.BooleanField(default=False,
                                      help_text='shows if user got dividend',
                                      verbose_name='dividend status')

    class Meta:
        verbose_name = "Дивиденд пользователя"
        verbose_name_plural = "Дивиденды пользователей"
        ordering = ['dividend']

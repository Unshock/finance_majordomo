from django.db import models
from django.core.validators import MinLengthValidator
from django.urls import reverse
from ..assets.models import Asset
from django.utils.translation import gettext_lazy as _

from ..users.models import User


class Stock(Asset):

    ticker = models.CharField(
        max_length=10,
        verbose_name="Тикер акции",
        unique=True
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Имя акции"
    )

    isin = models.CharField(
        max_length=100,
        verbose_name="ISIN",
        blank=True,
        unique=True
    )

    currency = models.CharField(
        max_length=10,
        verbose_name="Валюта номинала",
        blank=True
    )

    issuedate = models.DateField(
        verbose_name="Дата начала торгов",
        blank=True
    )

    latname = models.CharField(
        max_length=100,
        verbose_name="Английское наименование",
        blank=True
    )

    isqualifiedinvestors = models.BooleanField(
        verbose_name="Бумаги для квалифицированных инвесторов",
        blank=True
    )

    morningsession = models.BooleanField(
        verbose_name="Допуск к утренней дополнительной торговой сессии",
        blank=True
    )

    eveningsession = models.BooleanField(
        verbose_name="Допуск к вечерней дополнительной торговой сессии",
        blank=True
    )

    typename = models.CharField(
        max_length=100,
        verbose_name="Вид/категория ценной бумаги",
        blank=True
    )

    group = models.CharField(
        max_length=100,
        verbose_name="Код типа инструмента",
        blank=True
    )

    type = models.CharField(
        max_length=100,
        verbose_name="Тип бумаги",
        blank=True
    )

    groupname = models.CharField(
        max_length=100,
        verbose_name="Тип инструмента",
        blank=True
    )

    stock_data = models.JSONField(
        verbose_name="Данные об акции")

    latest_dividend_update = models.DateField(
        verbose_name='Дата последнего обновления информации о дивидендах',
        blank=True,
        null=True
    )

    users = models.ManyToManyField(
        User,
        through='StocksOfUser',
        through_fields=('stock', 'user'),
        blank=True,
        related_name='stock',
    )

    def __str__(self):
        return self.latname

    def get_delete_url(self):
        return reverse("delete_stock", kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ['creation_date', 'ticker', 'name']


class StocksOfUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Акции пользователя"
        verbose_name_plural = "Акции пользователей"
        ordering = ['stock']


class ProdCalendar(models.Model):

    date_status_choice = [
        ('0', 'Working'),
        ('1', 'Nonworking'),
    ]

    date = models.DateField(
        max_length=10,
        verbose_name='Дата'
    )

    date_status = models.CharField(
        max_length=10,
        choices=date_status_choice,
        verbose_name='Статус дня'
    )

    class Meta:
        ordering = ['date', 'date_status']



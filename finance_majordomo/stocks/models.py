from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Stock(models.Model):
    creation_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")
    ticker = models.CharField(
        max_length=10, verbose_name="Тикер акции", unique=True)
    name = models.CharField(
        max_length=100, verbose_name="Имя акции")
    #сделать сессионс дата
    stock_data = models.JSONField(
        verbose_name="Данные об акции")

    def __str__(self):
        return self.name

    def get_delete_url(self):
        return reverse("delete_stock", kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ['creation_date', 'ticker', 'name']


class ProdCalendar(models.Model):

    date_status_choice = [
        ('0', 'Working'),
        ('1', 'Nonworking'),
    ]

    date = models.CharField(max_length=10, verbose_name='Дата')
    date_status = models.CharField(max_length=10, choices=date_status_choice, verbose_name='Статус дня')

    class Meta:
        ordering = ['date', 'date_status']



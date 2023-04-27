from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from finance_majordomo.stocks.models import Stock


class User(AbstractUser):
    creation_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Creation_date"))
    stocks = models.ManyToManyField(
        Stock,
        through='UsersStocks',
        through_fields=('user', 'stock'),
        blank=True,
        related_name='users',
    )
    fields_to_display = models.JSONField(
        verbose_name='Поля для отображения',
        blank=True,
        null=True
    )

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def get_update_url(self):
        return reverse("update_user", kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse("delete_user", kwargs={'pk': self.pk})


class UsersStocks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE,
                              null=True)

    #не используется
    quantity = models.IntegerField(null=True, blank=True)


    class Meta:
        verbose_name = "Акция пользователя"
        verbose_name_plural = "Акции пользователей"
        ordering = ['stock']


import json

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .utils.fields_to_display import get_default_display_options


class User(AbstractUser):
    creation_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Creation_date")
    )

    # fields_to_display = models.JSONField(
    #     verbose_name='Поля для отображения',
    #     default=json.dumps(get_default_display_options())
    # )

    def get_current_portfolio(self):
        return self.portfolio_set.filter(is_current=True).last()

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def get_update_url(self):
        return reverse("update_user", kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse("delete_user", kwargs={'pk': self.pk})


class Portfolio(models.Model):
    creation_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Creation_date")
    )

    name = models.CharField(
        max_length=100,
        verbose_name=_("Portfolio name")
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Portfolio owner"
    )

    is_current = models.BooleanField(
        verbose_name=_("If the portfolio is current for the owner. The "
                       "current portfolio is used to work with transactions")
    )

    def get_assets_of_portfolio(self):
        return self.asset.all()

    class Meta:
        unique_together = ('name', 'user')


class UserSettings(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    show_ticker = models.BooleanField(default=True)
    show_name = models.BooleanField(default=True)
    show_currency = models.BooleanField(default=True)
    show_quantity = models.BooleanField(default=True)
    show_purchase_price = models.BooleanField(default=True)
    show_current_price = models.BooleanField(default=True)
    show_dividends_received = models.BooleanField(default=True)
    show_money_result_without_divs = models.BooleanField(default=True)
    show_money_result_with_divs = models.BooleanField(default=True)
    show_percent_result = models.BooleanField(default=True)
    show_rate_of_return = models.BooleanField(default=True)

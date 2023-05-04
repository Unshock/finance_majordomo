from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


def get_default_display_options():
    fields = {'ticker': True,
              'name': True,
              'currency': True,
              'quantity': True,
              'purchase_price': True,
              'current_price': True,
              'dividends_received': True,
              'percent_result': True,
              }
    return fields


class User(AbstractUser):
    creation_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Creation_date"))

    fields_to_display = models.JSONField(
        verbose_name='Поля для отображения',
        default=get_default_display_options()
    )

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def get_update_url(self):
        return reverse("update_user", kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse("delete_user", kwargs={'pk': self.pk})

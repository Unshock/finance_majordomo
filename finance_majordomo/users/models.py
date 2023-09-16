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

    fields_to_display = models.JSONField(
        verbose_name='Поля для отображения',
        default=json.dumps(get_default_display_options())
    )

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

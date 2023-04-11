from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Stock(models.Model):
    creation_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")


    # def __str__(self):
    #     return self.name

    # def get_delete_url(self):
    #     return reverse("delete_stock", kwargs={'pk': self.pk})

    # class Meta:
    #     verbose_name = "Акция"
    #     verbose_name_plural = "Акции"
    #     ordering = ['creation_date', 'ticker', 'name']

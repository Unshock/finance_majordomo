from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock

from common.utils.stocks import validate_ticker


class StockForm(ModelForm):
    ticker = forms.CharField(
        label='Тикер', widget=forms.TextInput(
            attrs={"class": "form-control"})
    )

    class Meta:
        model = Stock
        fields = ['ticker']

    def clean_ticker(self):
        ticker = self.cleaned_data['ticker']
        validated_ticker = validate_ticker(ticker)

        if not validated_ticker:
            raise ValidationError(_(f"Тикер {ticker} не найден"))
        return validated_ticker['ticker']

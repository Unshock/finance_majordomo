from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock

from common.utils.stocks import validate_ticker, get_asset_description


#to delete
class StockForm(ModelForm):

    ticker = forms.CharField(
        label='Тикер', widget=forms.TextInput(
            attrs={"class": "form-control"})
    )

    class Meta:
        model = Stock
        fields = ['ticker']

    def clean_ticker(self):
        ticker = self.cleaned_data['ticker'].upper()

        if Stock.objects.filter(secid=ticker).count() == 1:
            raise ValidationError(_(f"Тикер {ticker} уже добавлен"))

        stock_description = get_asset_description(ticker)

        if not stock_description:
            raise ValidationError(_(f"Ticker {ticker} hasn't been found"))

        if stock_description.get("GROUP") not in ["stock_shares", "stock_bonds"]:
            raise ValidationError(_(f"Only shares and bonds accepted"))

        self.cleaned_data['stock_description'] = stock_description
        return ticker

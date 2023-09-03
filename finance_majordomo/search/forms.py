from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock

from common.utils.stocks import validate_ticker, get_stock_description


class SearchForm(forms.Form):

    search_data = forms.CharField(
        label='Ticker, ISIN or name',
        widget=forms.TextInput(attrs={"class": "form-control"})
    )



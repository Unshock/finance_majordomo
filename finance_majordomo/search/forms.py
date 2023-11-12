from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock



class SearchForm(forms.Form):

    search_data = forms.CharField(
        label='Ticker, ISIN or name',
        widget=forms.TextInput(attrs={"class": "form-control"})
    )


class SearchResultForm(forms.Form):

    secid = forms.CharField(disabled=True)
    shortname = forms.CharField(disabled=True)
    regnumber = forms.CharField(disabled=True)
    name = forms.CharField(disabled=True)
    isin = forms.CharField(disabled=True, widget=forms.TextInput(attrs={"class": "form-label"}))
    type = forms.CharField(disabled=True, widget=forms.HiddenInput)
    group = forms.CharField(disabled=True, widget=forms.HiddenInput)
    primary_boardid = forms.CharField(disabled=True, widget=forms.HiddenInput)



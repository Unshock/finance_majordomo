from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock
from finance_majordomo.transactions.models import Transaction
from finance_majordomo.stocks.views import UsersStocks

from common.utils.stocks import validate_ticker


class TransactionForm(ModelForm):
    asset_type = forms.ChoiceField(
        label=_('Asset type'),
        choices=Transaction.asset_type_choices,
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
    )

    transaction_type = forms.ChoiceField(
        label=_('Transaction type'),
        choices=Transaction.transaction_type_choices,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
    )

    ticker = forms.ModelChoiceField(
        label=_('Ticker'),
        queryset=Stock.objects.all(),
        empty_label=_('Choose stock from the list'),

        )


    date = forms.CharField(
        label=_('Date'),
        widget=forms.TextInput(
            attrs={"class": "form-control",
                   "placeholder": _('YYYY-MM-DD'),
                   "rows": "10",
                   "cols": "40",
                   }
        ),
    )

    price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label=_('Price'),
        widget=forms.TextInput(
            attrs={"class": "form-control",
                   "rows": "10",
                   "cols": "40",
                   }
        )
    )

    fee = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label=_('Fee'),
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
        required=False
    )

    quantity = forms.IntegerField(
        label=_('Quantity'),
        widget=forms.TextInput(
            attrs={"class": "form-control",
                   "rows": "10",
                   "cols": "40",
                   }
        )
    )

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError(_("Price must be more than 0"))
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError(_("Quantity must be more than 0"))
        return quantity

    def clean_fee(self):
        fee = self.cleaned_data.get('fee')
        if fee is not None and fee < 0:
            raise ValidationError(_("Fee must be more or equal 0"))
        return fee

    class Meta:
        model = Transaction
        fields = [
            'transaction_type',
            'asset_type',
            'ticker',
            'date',
            'price',
            'fee',
            'quantity',
        ]


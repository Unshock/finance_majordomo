from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock
from finance_majordomo.transactions.models import Transaction
from finance_majordomo.stocks.views import UsersStocks

from common.utils.stocks import validate_ticker, get_stock_description

from bootstrap4.widgets import RadioSelectButtonGroup


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class TransactionForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'

        self.helper.add_input(Submit('submit', 'Submit'))

    asset_type = forms.ChoiceField(
        label=_('Asset type'),
        choices=Transaction.asset_type_choices,
        widget=forms.Select(
            #attrs={"class": "form-control"}
        ),
    )

    transaction_type = forms.ChoiceField(
        #initial='BUY',

        label=_('Transaction type'),
        choices=Transaction.transaction_type_choices,

        widget=RadioSelectButtonGroup(
            # тут опции для каждой радио кнопки - хотелось бы расположить их все отцентрованно
            attrs={'class': 'form-check-inline d-inline-flex justify-content-center',

                   }
        ),
    )

    ticker = forms.ModelChoiceField(
        label=_('Share'),
        queryset=Stock.objects.all(),
        empty_label=_('Choose stock from the list'),

        )

    # ticker_new = forms.CharField(
    #     label=_("Ticker"),
    # )

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

    # def clean_ticker(self):
    #     ticker = self.cleaned_data['ticker_new'].upper()
    # 
    #     # if Stock.objects.filter(ticker=ticker).count() == 1:
    #     #     raise ValidationError(_(f"Тикер {ticker} уже добавлен"))
    # 
    #     stock_description = get_stock_description(
    #         self.cleaned_data.get('ticker'))
    # 
    #     if not stock_description:
    #         raise ValidationError(_(f"Ticker {ticker} hasn't been found"))
    # 
    #     if stock_description.get("GROUP") != "stock_shares":
    #         raise ValidationError(_(f"Only shares accepted"))
    # 
    #     self.cleaned_data['stock_description'] = stock_description
    #     return ticker

    class Meta:
        model = Transaction
        fields = [
            'transaction_type',
            'asset_type',
            'ticker',
            #'ticker_new',
            'date',
            'price',
            'fee',
            'quantity',
        ]


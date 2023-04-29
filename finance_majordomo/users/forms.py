from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

from finance_majordomo.users.models import User


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(
        label=_('Username'), widget=forms.TextInput(
            attrs={"class": "form-control"}
        )
    )
    first_name = forms.CharField(
        label=_('First name'), widget=forms.TextInput(
            attrs={"class": "form-control"}
        )
    )
    last_name = forms.CharField(
        label=_('Last name'), widget=forms.TextInput(
            attrs={"class": "form-control"}
        )
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2'
        ]


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label=_("Username"), widget=forms.TextInput(
        attrs={"class": "form-control"}))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput(
        attrs={"class": "form-control"}))


class FieldsUserForm(forms.Form):

    ticker = forms.BooleanField(
        required=False,
        )
    name = forms.BooleanField(
        required=False,
        )
    currency = forms.BooleanField(
        required=False,
        )
    quantity = forms.BooleanField(
        required=False,
        )
    purchase_price = forms.BooleanField(
        required=False,
        )
    current_price = forms.BooleanField(
        required=False,
        )
    money_result_without_divs = forms.BooleanField(
        required=False,
        )
    percent_result = forms.BooleanField(
        required=False,
        )
    dividends_received = forms.BooleanField(
        required=False,
        )
    money_result_with_divs = forms.BooleanField(
        required=False,
        )
    rate_of_return = forms.BooleanField(
        required=False
    )

    class Meta:
        fields = [
            'ticker',
            'name',
            'currency',
            'quantity',
            'purchase price',
            'current price',
            'dividends_received',
            'money_result_without_divs',
            'money_result_with_divs',
            'percent_result',
            'rate_of_return',
        ]


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from finance_majordomo.users.utils.fields_to_display import FIELDS_TO_DISPLAY
from .models import User, UserSettings


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

    for field in FIELDS_TO_DISPLAY:
        locals()[field] = forms.BooleanField(required=False)

    class Meta:
        fields = FIELDS_TO_DISPLAY
        
#         
# class UserSettingsForm(forms.Form):
#     show_ticker = forms.BooleanField(required=False)
# 
#     def __init__(self, *args, **kwargs):
#         self.user = kwargs.pop('user', None)
#         super(UserSettingsForm, self).__init__(*args, **kwargs)
# 
#         if self.user:
#             try:
#                 user_settings = UserSettings.objects.get(user=self.user)
#                 self.fields['show_ticker'].initial = user_settings.show_ticker
#             except UserSettings.DoesNotExist:
#                 pass


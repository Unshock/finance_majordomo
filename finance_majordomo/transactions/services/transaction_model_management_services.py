from service_objects.fields import ModelField
from service_objects.services import Service
from django import forms

from finance_majordomo.stocks.models import Asset
from finance_majordomo.transactions.models import Transaction
from django.utils.translation import gettext_lazy as _

from finance_majordomo.users.models import User


class CreateTransactionService(Service):
    transaction_type = forms.ChoiceField(choices=Transaction.transaction_type_choices)
    date = forms.DateField()
    price = forms.DecimalField(max_digits=8, decimal_places=2)
    fee = forms.DecimalField(max_digits=8, decimal_places=2, required=False)
    quantity = forms.IntegerField()
    asset = ModelField(Asset)

    accrued_interest_required = forms.BooleanField()
    user = ModelField(User)

    if accrued_interest_required:
        print(accrued_interest_required, asset, '2222222222222222222222')
        accrued_interest = forms.DecimalField(
            max_digits=8, decimal_places=2, required=True)

    else:
        accrued_interest = forms.DecimalField(
            max_digits=8, decimal_places=2, required=False)

    def process(self):
        transaction_type = self.cleaned_data['transaction_type']
        date = self.cleaned_data['date']
        price = self.cleaned_data['price']
        fee = self.cleaned_data['fee']
        quantity = self.cleaned_data['quantity']
        asset = self.cleaned_data['asset']
        accrued_interest = self.cleaned_data.get('accrued_interest')


        print(self.cleaned_data.items())
        self.a = 'a'
        
              # CreateBookingService.execute({
              #     'name': form.cleaned_data['name'],
              #     'email': form.cleaned_data['email'],
              #     'checkin_date': form.cleaned_data['checkin_date'],
              #     'checkout_date': form.cleaned_data['checkout_date'],
              # })
        # Update or create a customer
        # customer = Customer.objects.update_or_create(
        #     email=email,
        #     defaults={
        #         'name': name
        #     }
        # )

        # # Create booking
        # self.booking = Booking.objects.create(
        #     customer=customer,
        #     checkin_date=checkin_date,
        #     checkout_date=checkout_date,
        #     status=Booking.PENDING_VERIFICATION,
        # )

        return self.a

    def post_process(self):
        # Send verification email (check out django-herald)
        print("POSTPROCESS")
        #VerifyEmailNotification(self.booking).send()
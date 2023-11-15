from datetime import datetime
from decimal import Decimal

from service_objects.fields import ModelField
from service_objects.services import Service

from finance_majordomo.dividends.models import Dividend, DividendsOfPortfolio
from finance_majordomo.stocks.models import Asset
from finance_majordomo.users.models import Portfolio


class TogglePortfolioDividendService(Service):

    dividend = ModelField(Dividend)
    portfolio = ModelField(Portfolio)

    def process(self):
        dividend = self.cleaned_data['dividend']
        portfolio = self.cleaned_data['portfolio']

        dividend_of_portfolio = DividendsOfPortfolio.objects.get(
            portfolio=portfolio, dividend=dividend
        )

        if dividend_of_portfolio.is_received:
            dividend_of_portfolio.is_received = False
            dividend_of_portfolio.save()

        else:
            dividend_of_portfolio.is_received = True
            dividend_of_portfolio.save()


class FillAccrualModel(Service):

    def __init__(self, *args, **kwargs):
        self.accruals_dict = kwargs.pop('accruals_dict')
        super(FillAccrualModel, self).__init__(*args, **kwargs)

    asset = ModelField(Asset)

    def process(self):
        self.asset = self.cleaned_data.get('asset')
        self._fill_accrual_model()

    def _get_self_asset_type(self):
        types_dict = {
            'preferred_share': 'preferred_share',
            'common_share': 'common_share',
            'ofz_bond': 'bond',
            'corporate_bond': 'bond'
        }

        return types_dict.get(self.asset.type)

    def _fill_accrual_model(self):
        asset_type = self._get_self_asset_type()

        for date, accrual_value in self.accruals_dict.items():

            if accrual_value[asset_type]['div']:
                amount = accrual_value[asset_type]['value']

            else:
                continue

            try:
                existing_div = Dividend.objects.get(asset=self.asset, date=date)

                if not existing_div.amount == amount:
                    print('Dividend has been changed while updating. '
                          'Probably mistake!')
                continue

            except Dividend.DoesNotExist:
                self._create_accrual_model_item(date, amount)

        self.asset.latest_accrual_update = datetime.today()
        self.asset.latest_dividend_update = datetime.today()
        self.asset.save()

    def _create_accrual_model_item(self, date, amount):
        dividend = Dividend.objects.create(
            date=date,
            asset=self.asset,
            amount=amount
        )
        dividend.save()

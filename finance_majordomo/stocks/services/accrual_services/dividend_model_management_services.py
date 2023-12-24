from datetime import datetime

from service_objects.fields import ModelField
from service_objects.services import Service

from finance_majordomo.stocks.models.accrual_models import Accrual, AccrualsOfPortfolio
from finance_majordomo.stocks.models.asset import Asset
from finance_majordomo.stocks.models.transaction_models import Transaction
from finance_majordomo.stocks.services.transaction_services.transaction_calculation_services import \
    get_asset_quantity_for_portfolio
from finance_majordomo.users.models import Portfolio


def execute_toggle_portfolio_accrual_service(accrual: Accrual,
                                             portfolio: Portfolio):
    """
    :param accrual: Accrual model object
    :param portfolio: Portfolio model object
    :return: returns nothing but toggles receiving (received/not received) of 
        specified Accrual in specified Portfolio
    """

    TogglePortfolioDividendService.execute({
        'accrual': accrual,
        'portfolio': portfolio
    })


class TogglePortfolioDividendService(Service):

    accrual = ModelField(Accrual)
    portfolio = ModelField(Portfolio)

    def process(self):
        accrual = self.cleaned_data['accrual']
        portfolio = self.cleaned_data['portfolio']

        accrual_of_portfolio = AccrualsOfPortfolio.objects.get(
            portfolio=portfolio, accrual=accrual
        )

        if accrual_of_portfolio.is_received:
            accrual_of_portfolio.is_received = False
            accrual_of_portfolio.save()


        else:
            accrual_of_portfolio.is_received = True
            accrual_of_portfolio.save()



def execute_accrual_model_data_filling_service(
        asset: Asset, accrual_data_dict: dict):
    """
    :param asset: Asset model object
    :param accrual_data_dict: dictionary of accruals data like:
        {
          '2023-12-03': {
            'common_share': {
              'div': True,
              'value': Decimal('15.80')
            },
            'preferred_share': {
              'div': False,
              'value': Decimal('0')
            }
          },
          '2022-05-08': {
            'common_share': {
              'div': True,
              'value': Decimal('14.4')
            },
          'preferred_share': {
              'div': True,
              'value': Decimal('14.4')
            }
          }
        }
    :return: returns nothing fills Accrual model of Asset with accruals from
        specified accrual dictionary
    """
    AccrualModelDataFillingService.execute({
        'asset': asset,
    }, accrual_data_dict=accrual_data_dict)


class AccrualModelDataFillingService(Service):

    def __init__(self, *args, **kwargs):
        self.accrual_data_dict = kwargs.pop('accrual_data_dict')
        super().__init__(*args, **kwargs)

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

        for date, accrual_value in self.accrual_data_dict.items():

            if not accrual_value[asset_type]['div']:
                continue

            amount = accrual_value[asset_type]['value']

            try:
                existing_accrual = Accrual.objects.get(
                    asset=self.asset, date=date)

                if existing_accrual.amount != amount:
                    print('Dividend has been changed while updating. '
                          'Probably mistake!')
                    # logging!
                continue

            except Accrual.DoesNotExist:
                self._create_accrual_model_item(date, amount)

        self.asset.latest_accrual_update = datetime.today()
        self.asset.save()

    def _create_accrual_model_item(self, date, amount):
        dividend = Accrual.objects.create(
            date=date,
            asset=self.asset,
            amount=amount
        )
        dividend.save()


def execute_update_accruals_of_portfolio(
        portfolio: Portfolio, transaction: Transaction, action_type: str):
    """
    :param portfolio: Portfolio model object
    :param transaction: Transaction model object
    :param action_type: type of the action that calls the service
    :return: adding of deleting Transaction offers changes of accruals of
        the specified portfolio so the func updates portfolio accrual data.
        If during the transaction the number of assets on the day of the
        accrual becomes zero, then the status of receiving the accrual
        becomes negative; otherwise, if the transaction adds an asset,
        the portfolio dividend appears but its status remains negative
    """
    action_type_list = ['add_transaction',
                        'del_transaction',
                        'update_transaction'
                        ]

    if action_type not in action_type_list:
        raise ValueError('Invalid action type')

    UpdateAccrualsOfPortfolio.execute({
        'portfolio': portfolio,
        'transaction': transaction
    }, action_type=action_type)


class UpdateAccrualsOfPortfolio(Service):

    def __init__(self, *args, **kwargs):
        self.action_type = kwargs.pop('action_type') # переделать на forms.choice
        super().__init__(*args, **kwargs)

    portfolio = ModelField(Portfolio)
    transaction = ModelField(Transaction)

    def process(self):

        self.portfolio = self.cleaned_data.get('portfolio')
        self.transaction = self.cleaned_data.get('transaction')

        self._update_accruals_of_portfolio(
            self._get_accruals_the_transaction_affects()
        )

    def _get_accruals_the_transaction_affects(self):
        asset = self.transaction.asset
        date = self.transaction.date

        return Accrual.objects.filter(asset=asset, date__gte=date)

    def _create_accrual_of_portfolio(self, accrual):

        AccrualsOfPortfolio.objects.create(
            portfolio=self.portfolio,
            accrual=accrual,
            is_received=False
        )

    def _update_accruals_of_portfolio(self, accruals):

        tr_type = self.transaction.transaction_type
        quantity = self.transaction.quantity
        asset = self.transaction.asset

        for accrual in accruals:

            # asset quantity for the accrual date
            accrual_date_quantity = get_asset_quantity_for_portfolio(
                self.portfolio, asset, accrual.date
            )

            # if we DELETE "BUY" transaction that can cause zero asset quantity
            if tr_type == 'BUY' and self.action_type == 'del_transaction':
                accrual_date_quantity -= quantity

            try:
                dividend_of_portfolio = AccrualsOfPortfolio.objects.get(
                    portfolio=self.portfolio,
                    accrual=accrual)

                if accrual_date_quantity == 0:
                    dividend_of_portfolio.is_received = False
                    dividend_of_portfolio.save()

            except AccrualsOfPortfolio.DoesNotExist:
                self._create_accrual_of_portfolio(accrual)

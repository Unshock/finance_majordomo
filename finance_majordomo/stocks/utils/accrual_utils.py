import django
import os

from finance_majordomo.stocks.services.transaction_services.transaction_calculation_services import get_asset_quantity_for_portfolio
from finance_majordomo.users.utils.utils import get_current_portfolio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_majordomo.settings')
django.setup()

from finance_majordomo.stocks.models.models import Dividend, DividendsOfUser, DividendsOfPortfolio


def update_dividends_of_user(request, asset_obj, date=None, transaction=None):

    asset_dividends = Dividend.objects.filter(asset=asset_obj.id)
    portfolio = get_current_portfolio(request.user)
    print(asset_dividends, 'tttttttttttttttttttttttttttttttt')

    if date:
        asset_dividends = asset_dividends.filter(date__gte=date)

    # users_dividends = Dividend.objects.filter(
    #     stock=stock_obj.id,
    #     id__in=request.user.dividendsofuser_set.values_list(
    #         'dividend'))

    for div in asset_dividends:

        quantity = get_asset_quantity_for_portfolio(
            portfolio.id, asset_obj.id, date=div.date)\
                   - transaction.quantity

        try:
            dividend_of_user = DividendsOfUser.objects.get(
                user=request.user,
                dividend=div)

            if quantity <= 0:
                dividend_of_user.is_received = False

        except DividendsOfUser.DoesNotExist:
            dividend_of_user = DividendsOfUser.objects.create(
                user=request.user,
                dividend=div,
                is_received=False
            )
        print(dividend_of_user)
        dividend_of_user.save()


def update_dividends_of_portfolio(
        portfolio, asset_id, date=None, transaction=None):

    asset_dividends = Dividend.objects.filter(asset=asset_id)

    if date:
        asset_dividends = asset_dividends.filter(date__gte=date)

    for div in asset_dividends:

        tr_quantity = transaction.quantity if transaction.transaction_type == \
                                           'BUY' else transaction.quantity * -1

        quantity = get_asset_quantity_for_portfolio(
            portfolio.id, asset_id, date=div.date) + tr_quantity
        
        print('DIVIDEND QUANTITTY', quantity, tr_quantity, quantity - tr_quantity)
        
        try:
            dividend_of_portfolio = DividendsOfPortfolio.objects.get(
                portfolio=portfolio,
                dividend=div)

            if quantity <= 0:
                dividend_of_portfolio.is_received = False

        except DividendsOfPortfolio.DoesNotExist:
            dividend_of_portfolio = DividendsOfPortfolio.objects.create(
                portfolio=portfolio,
                dividend=div,
                is_received=False
            )
        print(dividend_of_portfolio)
        dividend_of_portfolio.save()

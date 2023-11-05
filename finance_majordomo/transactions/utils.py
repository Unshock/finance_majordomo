from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from collections import deque
from typing import List

from django.db.models import QuerySet, Sum

from .models import Transaction
from ..currencies.utils import get_usd_rate
from ..stocks.models import Asset

from ..users.models import User, Portfolio
from ..users.utils.utils import get_current_portfolio


def get_quantity(user: User,
                 asset_obj: Asset,
                 date: datetime.date = None) -> Decimal:

    asset_id = asset_obj.id

    users_specific_asset_transactions = Transaction.objects.filter(
        user=user, ticker=asset_id).order_by('date')

    # users_transactions = Transaction.objects.filter(
    #    user=User.objects.get(id=request.user.iget_quantityd))
    # users_specific_asset_transactions = users_transactions.filter(
    #    ticker=Stock.objects.get(id=stock_id)).order_by('date')
    # print(users_specific_asset_transactions, '1')

    if date:
        users_specific_asset_transactions = \
            users_specific_asset_transactions.filter(date__lte=date)

    quantity = Decimal('0')
    date = None
    #previous_date = None

    for transaction in users_specific_asset_transactions:

        previous_date = date
        date = transaction.date

        if date != previous_date and quantity < 0:
            raise ValueError('quantity can\'t be lower than 0')

        if transaction.transaction_type == "BUY":
            quantity += transaction.quantity
        elif transaction.transaction_type == "SELL":
            if previous_date is None:
                raise ValueError('quantity cant be lower than 0')
            quantity -= transaction.quantity
        else:
            raise Exception('not buy or sell found')

    return quantity


def get_quantity2(portfolio_id: int,
                 asset_id: int,
                 date: datetime.date = None) -> Decimal:

    users_specific_asset_transactions = Transaction.objects.filter(
        portfolio=portfolio_id, asset=asset_id).order_by('date')

    # users_transactions = Transaction.objects.filter(
    #    user=User.objects.get(id=request.user.iget_quantityd))
    # users_specific_asset_transactions = users_transactions.filter(
    #    ticker=Stock.objects.get(id=stock_id)).order_by('date')
    # print(users_specific_asset_transactions, '1')

    if date:
        users_specific_asset_transactions = \
            users_specific_asset_transactions.filter(date__lte=date)

    quantity = Decimal('0')
    date = None
    #previous_date = None

    for transaction in users_specific_asset_transactions:

        previous_date = date
        date = transaction.date

        if date != previous_date and quantity < 0:
            raise ValueError('quantity can\'t be lower than 0')

        if transaction.transaction_type == "BUY":
            quantity += transaction.quantity
        elif transaction.transaction_type == "SELL":
            if previous_date is None:
                raise ValueError('quantity cant be lower than 0')
            quantity -= transaction.quantity
        else:
            raise Exception('not buy or sell found')

    return quantity


@dataclass
class TransactionItem:
    quantity: Decimal
    price: Decimal
    date: datetime.date


def _get_portfolio_asset_purchase_list(
        portfolio_asset_transactions: QuerySet) -> List[TransactionItem]:

    portfolio_asset_sell_transactions = portfolio_asset_transactions.filter(
        transaction_type='BUY')

    purchase_list = []

    for transaction in portfolio_asset_sell_transactions:

        quantity = transaction.quantity
        price = transaction.price
        date = transaction.date

        purchase_list.append(
            TransactionItem(price=price, quantity=quantity, date=date)
        )

    return purchase_list


def _get_portfolio_asset_total_sold(
        portfolio_asset_transactions: QuerySet) -> int:

    quantity_of_sales = portfolio_asset_transactions.filter(
        transaction_type='SELL').aggregate(Sum('quantity')).get('quantity__sum')

    return quantity_of_sales if quantity_of_sales else Decimal('0')


def _get_purchase_price(purchase_list: List[TransactionItem],
                        total_sold: int, currency: str) -> Decimal:

    purchase_price = 0
    currency_rate = Decimal('1')

    for elem in purchase_list:
        if elem.quantity >= total_sold:
            elem.quantity -= total_sold
            total_sold = 0

        else:
            sold = elem.quantity
            elem.quantity = 0
            total_sold -= sold

        if currency == 'usd':
            currency_rate = get_usd_rate(elem.date)

        purchase_price += elem.quantity * elem.price / currency_rate

        if total_sold < 0:
            raise Exception('тотал меньше 0')

    return Decimal(purchase_price)


def get_purchase_price(portfolio_id: int, asset_id: int,
                       currency: str = None,
                       date: datetime.date = None) -> Decimal:

    portfolio_asset_transactions = Transaction.objects.filter(
        portfolio=portfolio_id,
        asset=asset_id).order_by('date')
    
    if date:
        portfolio_asset_transactions = \
            portfolio_asset_transactions.filter(date__lte=date)

    purchase_list = _get_portfolio_asset_purchase_list(
        portfolio_asset_transactions)
    total_sold = _get_portfolio_asset_total_sold(portfolio_asset_transactions)

    return _get_purchase_price(purchase_list, total_sold, currency)


def get_average_purchase_price(portfolio_id: int, asset_id: int,
                                currency: str = None,
                                date: datetime.date = None) -> Decimal:
    average_purchase_price = get_purchase_price(
        portfolio_id, asset_id, currency, date) / get_quantity2(
        portfolio_id, asset_id, date)

    return average_purchase_price


# # deque is BAD in this case - made for check should be rewritten
# def get_average_purchase_price(request, asset_obj, date=None) -> Decimal:
#     users_specific_asset_transactions = Transaction.objects.filter(
#         user=request.user,
#         ticker=asset_obj).order_by('date')
# 
#     if date:
#         users_specific_asset_transactions = \
#             users_specific_asset_transactions.filter(date__lte=date)
# 
#     transaction_deque = deque()
# 
#     for transaction in users_specific_asset_transactions:
# 
#         for _ in range(transaction.quantity):
# 
#             if transaction.transaction_type == "BUY":
#                 transaction_deque.append(transaction.price)
#             elif transaction.transaction_type == "SELL":
#                 transaction_deque.popleft()
# 
#     result = Decimal(sum(transaction_deque) / len(transaction_deque))
# 
#     return result


def validate_transaction(request, transaction: dict) -> bool:
    validator = transaction.get('validator')
    asset_obj = transaction.get('asset_obj')
    transaction_type = transaction.get('transaction_type')
    date = transaction.get('date')
    quantity = transaction.get('quantity')

    if transaction_type == 'SELL' and validator == 'delete_validator' or \
            transaction_type == 'BUY' and validator == 'add_validator':
        return True

    portfolio = get_current_portfolio(request.user)

    day_end_balance = get_quantity2(
        portfolio.id, asset_obj.id, date=date) - quantity

    if day_end_balance < 0:
        return False

    portfolio_transactions = Transaction.objects.filter(
        portfolio=portfolio,
        asset=asset_obj.id,
        date__gt=date).order_by('date')

    # that means the validated transaction would not affect any transactions:
    if portfolio_transactions.count() == 0:
        return True

    cur_date = date

    for transaction in portfolio_transactions:

        prev_date = cur_date
        cur_date = transaction.date

        if transaction.transaction_type == "BUY":
            day_end_balance += transaction.quantity
        elif transaction.transaction_type == "SELL":
            day_end_balance -= transaction.quantity
        # should not be raised
        else:
            raise Exception('not BUY or SELL found')

        if prev_date != cur_date and day_end_balance < 0:
            return False

    return False if day_end_balance < 0 else True

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

from django.db.models import QuerySet, Sum

from finance_majordomo.stocks.services.currency_services.currency_management_services import \
    get_currency_rate
from finance_majordomo.stocks.models.transaction_models import Transaction


def get_asset_quantity_for_portfolio(portfolio_id: int,
                                     asset_id: int,
                                     date: datetime.date = None) -> Decimal:

    users_specific_asset_transactions = Transaction.objects.filter(
        portfolio=portfolio_id, asset=asset_id).order_by('date')

    if date:
        users_specific_asset_transactions = \
            users_specific_asset_transactions.filter(date__lte=date)

    total_purchased = _get_portfolio_asset_total_purchased(
        users_specific_asset_transactions
    )

    total_sold = _get_portfolio_asset_total_sold(
        users_specific_asset_transactions
    )

    return total_purchased - total_sold


@dataclass
class TransactionItem:
    quantity: Decimal
    price: Decimal
    date: datetime.date


def _get_portfolio_asset_purchase_list(
        portfolio_asset_transactions: QuerySet) -> List[TransactionItem]:
    portfolio_asset_purchase_transactions = portfolio_asset_transactions.filter(
        transaction_type='BUY')

    purchase_list = []

    for transaction in portfolio_asset_purchase_transactions:
        quantity = transaction.quantity
        price = transaction.price
        date = transaction.date

        purchase_list.append(
            TransactionItem(price=price, quantity=quantity, date=date)
        )

    return purchase_list


def _get_portfolio_asset_total_purchased(
        portfolio_asset_transactions: QuerySet) -> Decimal:
    quantity_of_purchases = portfolio_asset_transactions \
        .filter(transaction_type='BUY') \
        .aggregate(Sum('quantity')) \
        .get('quantity__sum')

    quantity_of_purchases = Decimal('0') \
        if quantity_of_purchases is None else Decimal(quantity_of_purchases)

    return quantity_of_purchases


def _get_portfolio_asset_total_sold(
        portfolio_asset_transactions: QuerySet) -> Decimal:
    quantity_of_sales = portfolio_asset_transactions \
        .filter(transaction_type='SELL') \
        .aggregate(Sum('quantity')) \
        .get('quantity__sum')

    quantity_of_sales = Decimal('0') \
        if quantity_of_sales is None else Decimal(quantity_of_sales)

    return quantity_of_sales


def _get_purchase_price(purchase_list: List[TransactionItem],
                        total_sold: Decimal, currency: str) -> Decimal:
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
            currency_rate = get_currency_rate(
                date_dt=elem.date, currency='usd')

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

    total_purchase_price = get_purchase_price(
        portfolio_id, asset_id, currency, date)

    quantity = get_asset_quantity_for_portfolio(portfolio_id, asset_id, date)

    return total_purchase_price / quantity

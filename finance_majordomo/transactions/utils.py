from decimal import Decimal

from .models import Transaction
from ..users.models import User


def get_quantity(request, asset_obj, date=None) -> int:

    stock_id = asset_obj.id

    users_specific_asset_transactions = Transaction.objects.filter(
        user=request.user, ticker=stock_id).order_by('date')

    #users_transactions = Transaction.objects.filter(
    #    user=User.objects.get(id=request.user.id))
    #users_specific_asset_transactions = users_transactions.filter(
    #    ticker=Stock.objects.get(id=stock_id)).order_by('date')
    # print(users_specific_asset_transactions, '1')

    if date:
        users_specific_asset_transactions = \
            users_specific_asset_transactions.filter(date__lte=date)

    quantity = 0
    date = None
    previous_date = None

    for transaction in users_specific_asset_transactions:
        if date != previous_date and quantity < 0:
            raise ValueError('quantity can\'t be lower than 0')

        previous_date = date
        date = transaction.date

        if transaction.transaction_type == "BUY":
            quantity += transaction.quantity
        elif transaction.transaction_type == "SELL":
            if previous_date is None:
                raise ValueError('quantity cant be lower than 0')
            quantity -= transaction.quantity
        else:
            raise Exception('not buy or sell found')
    return quantity


def get_purchace_price(request, stock_obj):
    # С учетом метода FIFO
    users_specific_asset_transactions = Transaction.objects.filter(
        user=request.user,
        ticker=stock_obj).order_by('date')

    purchase_list = []
    total_sold = 0
    purchase_price = 0

    for transaction in users_specific_asset_transactions:
        if transaction.transaction_type == "BUY":
            purchase_list.append({
                'quantity': transaction.quantity,
                'price': transaction.price
            })
        elif transaction.transaction_type == "SELL":
            total_sold += transaction.quantity
        else:
            raise Exception('not buy nor sell')

    for elem in purchase_list:
        #print('total_sold', total_sold)
        if elem['quantity'] >= total_sold:
            elem['quantity'] -= total_sold
            total_sold = 0

        else:
            sold = elem['quantity']
            elem['quantity'] = 0
            total_sold -= sold

        purchase_price += elem['quantity'] * elem['price']

        if total_sold < 0:
            raise Exception('тотал меньше 0')

    return Decimal(purchase_price)
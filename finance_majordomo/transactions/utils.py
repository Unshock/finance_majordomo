from decimal import Decimal
from collections import deque

from .models import Transaction
from ..users.models import User


def get_quantity(request, asset_obj, date=None) -> int:

    stock_id = asset_obj.id

    users_specific_asset_transactions = Transaction.objects.filter(
        user=request.user, ticker=stock_id).order_by('date')

    #users_transactions = Transaction.objects.filter(
    #    user=User.objects.get(id=request.user.iget_quantityd))
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
        #if date != previous_date and quantity < 0:
        #    raise ValueError('quantity can\'t be lower than 0')

        previous_date = date
        date = transaction.date

        if transaction.transaction_type == "BUY":
            quantity += transaction.quantity
        elif transaction.transaction_type == "SELL":
            #if previous_date is None:
            #    raise ValueError('quantity cant be lower than 0')
            quantity -= transaction.quantity
        else:
            raise Exception('not buy or sell found')
    return quantity


def get_purchase_price(request, stock_obj) -> Decimal:
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


# deque is BAD in this case - made for check should be rewritten
def get_average_purchase_price(request, asset_obj, date=None) -> Decimal:

    users_specific_asset_transactions = Transaction.objects.filter(
        user=request.user,
        ticker=asset_obj).order_by('date')

    if date:
        users_specific_asset_transactions = \
            users_specific_asset_transactions.filter(date__lte=date)

    transaction_deque = deque()

    for transaction in users_specific_asset_transactions:

        for _ in range(transaction.quantity):

            if transaction.transaction_type == "BUY":
                transaction_deque.append(transaction.price)
            elif transaction.transaction_type == "SELL":
                transaction_deque.popleft()

    result = Decimal(sum(transaction_deque) / len(transaction_deque))

    return result


def validate_transaction(request, transaction: dict) -> bool:

    validator = transaction.get('validator')
    asset_obj = transaction.get('asset_obj')
    transaction_type = transaction.get('transaction_type')
    date = transaction.get('date')
    quantity = transaction.get('quantity')

    if transaction_type == 'SELL' and validator == 'delete_validator' or \
            transaction_type == 'BUY' and validator == 'add_validator':
        return True

    day_end_balance = get_quantity(
        request, asset_obj, date=date) - quantity

    if day_end_balance < 0:
        return False

    users_transactions = Transaction.objects.filter(
        user=request.user,
        ticker=asset_obj.id,
        date__gt=date).order_by('date')

    # that means the validated transaction would not affect any transactions:
    if users_transactions.count() == 0:
        return True

    cur_date = date

    for transaction in users_transactions:

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


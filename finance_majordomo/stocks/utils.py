from decimal import Decimal

def get_money_result(current_price, purchace_price):
    return Decimal(current_price - purchace_price)
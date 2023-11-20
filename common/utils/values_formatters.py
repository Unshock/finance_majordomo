from decimal import Decimal
from moneyfmt import moneyfmt


def set_money_fmt(value: Decimal, places=2, curr='', sep=' ') -> str:
    return moneyfmt(value, places=places, curr=curr, sep=sep)


def set_percentage_fmt(value):
    return f'- {"{:.2%}".format(-value)}' if\
        value < 0 else f'+ {"{:.2%}".format(value)}'

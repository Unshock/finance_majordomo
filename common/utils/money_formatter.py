from decimal import Decimal
from moneyfmt import moneyfmt


def set_moneyfmt(value: Decimal, places=2, curr='', sep=' ') -> str:
    return moneyfmt(value, places=places, curr=curr, sep=sep)

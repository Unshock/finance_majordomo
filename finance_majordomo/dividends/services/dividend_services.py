from dataclasses import dataclass
from datetime import timedelta, datetime
from decimal import Decimal

from finance_majordomo.dividends.models import Dividend, DividendsOfUser


@dataclass
class DividendItem:
    div_obj: Dividend
    date_str: str
    quantity_for_the_date: int
    total_div: Decimal
    is_received: bool
    is_upcoming: bool


def get_user_accrual_list(user):

    date_today_dt = datetime.today().date()
    delta = timedelta(days=90)

    dividends_of_user = Dividend.objects.filter(
        id__in=user.dividendsofuser_set.values_list('dividend'),
        date__lte=date_today_dt + delta
    ).order_by('-date')

    list1 = []

    for div in dividends_of_user:
        list1.append(DividendItem)

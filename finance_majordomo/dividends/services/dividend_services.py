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



def get_context_data(self, *, object_list=None, **kwargs):
    context = super().get_context_data(**kwargs)
    context['page_title'] = _("Dividend list")

    dividend_list = []
    total_divs_payable = 0
    total_divs_received = 0
    total_divs_upcoming = 0

    user = self.request.user
    date_today_dt = datetime.today().date()

    delta = timedelta(days=90)

    dividends_of_user = Dividend.objects.filter(
        id__in=user.dividendsofuser_set.values_list('dividend'),
        date__lte=date_today_dt + delta
    ).order_by('-date')

    print(dividends_of_user, 'aYAYAYAYAYAYAYAYA')



    for div_obj in dividends_of_user:
        asset = div_obj.asset
        amount = div_obj.amount

        date_dt = div_obj.date
        date_str = datetime.strftime(date_dt, '%Y-%m-%d')


        is_upcoming = False if date_dt <= date_today_dt else True

        is_received = DividendsOfUser.objects.get(
            user=user, dividend=div_obj).is_received

        quantity_for_the_date = get_quantity(
            self.request.user, asset, date=date_str)

        if quantity_for_the_date > 0:
            total_div = Decimal(quantity_for_the_date * amount)

            if not is_upcoming:
                total_divs_payable += total_div
                total_divs_received += total_div if is_received else 0

            else:
                total_divs_upcoming += total_div

            dividend_list.append({
                'div_obj': div_obj,
                'date': date_str,
                'quantity': quantity_for_the_date,
                'total_div': total_div,
                'is_received': is_received,
                'is_upcoming': is_upcoming,
            })

    total_divs_payable = moneyfmt(
        total_divs_payable * Decimal(0.87), sep=' ')

    total_divs_received = moneyfmt(
        total_divs_received * Decimal(0.87), sep=' ')

    context['dividend_list'] = dividend_list
    context['total_divs_payable'] = total_divs_payable
    context['total_divs_received'] = total_divs_received
    context['total_divs_upcoming'] = total_divs_upcoming
    return context
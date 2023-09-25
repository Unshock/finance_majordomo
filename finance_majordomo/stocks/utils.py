from datetime import datetime, timedelta, timezone
from decimal import Decimal
from django.db.models import Max

from common.utils.stocks import get_date_status, get_stock_current_price, \
    get_stock_board_history
from finance_majordomo.stocks.models import SharesHistoricalData, ProdCalendar


def get_money_result(current_price, purchace_price):
    return Decimal(current_price - purchace_price)


def add_share_history_data_to_model(stock_obj, stock_board_history):

    for day_data in stock_board_history:

        SharesHistoricalData.objects.create(
            share=stock_obj,

            tradedate=day_data.get('TRADEDATE'),
            numtrades=day_data.get('NUMTRADES'),
            value=day_data.get('VALUE'),
            open=day_data.get('OPEN'),
            low=day_data.get('LOW'),
            high=day_data.get('HIGH'),
            legalcloseprice=day_data.get('LEGALCLOSEPRICE'),
            waprice=day_data.get('WAPRICE'),
            close=day_data.get('CLOSE'),
            volume=day_data.get('VOLUME'),
            waval=day_data.get('WAVAL'),
            trendclspr=day_data.get('TRENDCLSPR'),

            is_closed=True
        )


def get_prod_date(date: str):

    try:
        prod_date = ProdCalendar.objects.get(date=date)
    except ProdCalendar.DoesNotExist:

        try:
            date_status = get_date_status(date)
        except ConnectionError:
            raise ConnectionError('ne smog poluchit date status from internet')

        prod_date = ProdCalendar.objects.create(
            date=date,
            date_status=date_status
        )

    return prod_date


def update_historical_data(stock_obj: object, date=None):

    today_status = get_prod_date(
        datetime.strftime(datetime.today(), '%Y-%m-%d')).date_status

    today_date = datetime.today().date()

    latest_day = SharesHistoricalData.objects.filter(
        share=stock_obj).order_by('-tradedate')[0]

    latest_date_str = datetime.strftime(latest_day.tradedate, '%Y-%m-%d')

    gap_for_latest_day = (today_date - latest_day.tradedate).days

    if gap_for_latest_day < 0:
        raise Exception('gap cannot be < 0')
    # 
    # elif gap_for_latest_day == 0:
    #     update_today_data(stock_obj)

    elif not latest_day.is_closed and gap_for_latest_day > 0:
        update_history_data(stock_obj, date=latest_date_str)

    elif latest_day.is_closed and gap_for_latest_day > 1:

        for gap in range(1, gap_for_latest_day):
            date_str = datetime.datetime.strftime(
                (today_date - datetime.timedelta(gap)), '%Y-%m-%d')

            day_status = get_prod_date(date_str).date_status

            if day_status == 'Working':
                update_history_data(stock_obj, date=latest_date_str)

    if today_status == 'Working':
        update_today_data(stock_obj)


def update_history_data(stock_obj: object, date=None):

    stock_board_history = get_stock_board_history(
        stock_obj.ticker,
        start_date=date
    )

    for day_data in stock_board_history:

        date_dt = datetime.strptime(day_data.get('TRADEDATE'), "%Y-%m-%d")

        stock_historical_data, created = SharesHistoricalData.objects.get_or_create(
            tradedate=date_dt, share=stock_obj)

        stock_historical_data.numtrades = day_data.get('NUMTRADES')
        stock_historical_data.value = day_data.get('VALUE')
        stock_historical_data.open = day_data.get('OPEN')
        stock_historical_data.low = day_data.get('LOW')
        stock_historical_data.high = day_data.get('HIGH')
        stock_historical_data.legalcloseprice = day_data.get('LEGALCLOSEPRICE')
        stock_historical_data.waprice = day_data.get('WAPRICE')
        stock_historical_data.close = day_data.get('CLOSE')
        stock_historical_data.volume = day_data.get('VOLUME')
        stock_historical_data.waval = day_data.get('WAVAL')
        stock_historical_data.trendclspr = day_data.get('TRENDCLSPR')

        stock_historical_data.is_closed = True
        stock_historical_data.save()

        print(stock_historical_data, stock_historical_data.volume, created)


def update_today_data(stock_obj: object) -> object:

    # In minutes
    STANDARD_MOEX_LAG = 16
    UPDATE_TIME_MINUTES = 60 - STANDARD_MOEX_LAG
    EVENING_CUT_OFF = datetime.strptime(datetime.strftime(
        datetime.today(), '%Y-%m-%d 18:30:00'), '%Y-%m-%d %H:%M:%S')

    latest_day = SharesHistoricalData.objects.filter(
        share=stock_obj).order_by('-tradedate')[0]

    if latest_day.update_time:

        update_time_dt = datetime.strptime(
            datetime.strftime(latest_day.update_time, '%Y-%m-%d %H:%M:%S'),
            '%Y-%m-%d %H:%M:%S')

        # IF STOCK IS NOT ON EVENING SESSION AND UPDATE TIME LATER THAN
        # 18:30:00 TODAY => NO NEED TO UPDATE
        if not stock_obj.eveningsession and\
                update_time_dt > EVENING_CUT_OFF:
            return stock_obj

        # IF UPDATED RECENTLY => NO NEED TO UPDATE
        time_gap = get_time_gap(update_time_dt)
        print('time_gap', time_gap, stock_obj)
        if time_gap <= UPDATE_TIME_MINUTES:
            return stock_obj

    last_price_data = get_stock_current_price(stock_obj.ticker)

    today_dt = datetime.today().date()

    stock_today_price_data, _ = SharesHistoricalData.objects.get_or_create(
        tradedate=today_dt, share=stock_obj, defaults={
            'legalcloseprice': last_price_data[0],
            'is_closed': False,
            'update_time': last_price_data[1]
        })

    stock_today_price_data.legalcloseprice = last_price_data[0]
    stock_today_price_data.is_closed = False
    stock_today_price_data.update_time = last_price_data[1]

    stock_today_price_data.save()

    return stock_obj


def get_time_gap(update_time_dt):

    TIME_ZONE_DELTA = 3

    offset = timezone(timedelta(hours=TIME_ZONE_DELTA))
    current_time = datetime.now(offset)
    current_time_dt = datetime.strptime(
        datetime.strftime(current_time, '%Y-%m-%d %H:%M:%S'),
        '%Y-%m-%d %H:%M:%S')

    duration = current_time_dt - update_time_dt
    duration_in_s = duration.total_seconds()
    minutes = divmod(duration_in_s, 60)[0]

    return minutes
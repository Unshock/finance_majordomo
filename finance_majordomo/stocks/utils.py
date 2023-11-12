from datetime import datetime, timedelta, timezone
from decimal import Decimal
from django.db.models import Max

from common.utils.stocks import get_date_status, get_stock_current_price, \
    get_asset_board_history, get_current
from finance_majordomo.stocks.models import ProdCalendar, \
    AssetsHistoricalData, Asset


def get_money_result(current_price, purchace_price):
    return Decimal(current_price - purchace_price)


def get_asset_board(asset_type):
    boards_dict = {
        'ofz_bond': 'TQOB',
        'corporate_bond': 'TQCB',
        'exchange_bond': 'TQCB',
        'preferred_share': 'TQBR',
        'common_share': 'TQBR',
    }

    return boards_dict.get(asset_type)


def get_asset_market(asset_group):
    boards_dict = {
        'stock_shares': 'shares',
        'stock_bonds': 'bonds',
    }

    return boards_dict.get(asset_group)


def get_asset_history_data(asset, start_date=None):
    asset_history_data = get_asset_board_history(
        asset.secid,
        start_date=start_date,
        market=get_asset_market(asset.group),
        board=asset.primary_boardid)

    return asset_history_data[get_first_trade_date_index(asset_history_data):]


def get_first_trade_date_index(asset_history_data: list[dict]) -> int:
    for i, day in enumerate(asset_history_data):
        if day.get('LEGALCLOSEPRICE'):
            return i
    raise Exception('No tradedate found')


def add_share_history_data_to_model(stock_obj, asset_history_data):
    for day_data in asset_history_data:
        AssetsHistoricalData.objects.create(
            asset=Asset.objects.get(id=stock_obj.asset_ptr_id),

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
        
def add_share_history_data_to_model2(asset, asset_history_data):
    for day_data in asset_history_data:
        AssetsHistoricalData.objects.create(
            asset=Asset.objects.get(id=asset.id),

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


def add_bond_history_data_to_model(bond_obj, asset_history_data):
    #print(asset_history_data)

    for day_data in asset_history_data:
        AssetsHistoricalData.objects.create(
            asset=Asset.objects.get(id=bond_obj.asset_ptr_id),

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

            yieldclose=day_data.get("YIELDCLOSE"),
            couponpercent=day_data.get("COUPONPERCENT"),
            couponvalue=day_data.get("COUPONVALUE"),

            is_closed=True
        )

def add_bond_history_data_to_model2(asset, asset_history_data):
    #print(asset_history_data)

    for day_data in asset_history_data:
        AssetsHistoricalData.objects.create(
            asset=Asset.objects.get(id=asset.id),

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

            yieldclose=day_data.get("YIELDCLOSE"),
            couponpercent=day_data.get("COUPONPERCENT"),
            couponvalue=day_data.get("COUPONVALUE"),

            is_closed=True
        )


def get_prod_date(date: str) -> ProdCalendar:
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


def update_historical_data(asset_obj: object, date=None):
    related_obj = asset_obj.get_related_object()

    print(asset_obj, related_obj)

    today_status = get_prod_date(
        datetime.strftime(datetime.today(), '%Y-%m-%d')).date_status

    today_date = datetime.today().date()

    print(asset_obj, related_obj, type(related_obj))

    # ne tolko share no i bond
    latest_day = AssetsHistoricalData.objects.filter(
        asset=asset_obj).order_by('-tradedate')[0]

    print('latest_day', latest_day)

    latest_date_str = datetime.strftime(latest_day.tradedate, '%Y-%m-%d')

    gap_for_latest_day = (today_date - latest_day.tradedate).days

    if gap_for_latest_day < 0:
        raise Exception('gap cannot be < 0')
    # 
    # elif gap_for_latest_day == 0:
    #     update_today_data(stock_obj)

    elif not latest_day.is_closed and gap_for_latest_day > 0:
        update_history_data(asset_obj, date=latest_date_str)

    elif latest_day.is_closed and gap_for_latest_day > 1:

        for gap in range(1, gap_for_latest_day):
            delta_date_dt = (today_date - timedelta(gap))
            date_str = datetime.strftime(
                datetime(delta_date_dt.year,
                         delta_date_dt.month,
                         delta_date_dt.day), '%Y-%m-%d')

            day_status = get_prod_date(date_str).date_status

            if day_status == 'Working':
                update_history_data(asset_obj, date=latest_date_str)

    if today_status == 'Working':
        update_today_data(asset_obj)


def update_history_data(asset_obj: Asset, date=None):
    asset_history_data = get_asset_history_data(asset_obj, date)

    print('asset_history_data', asset_history_data)
    for day_data in asset_history_data:
        date_dt = datetime.strptime(day_data.get('TRADEDATE'), "%Y-%m-%d")

        # asset_obj = Asset.objects.get(asset_obj.asset)

        stock_historical_data, created = AssetsHistoricalData.objects.get_or_create(
            tradedate=date_dt, asset=asset_obj, defaults={
                'legalcloseprice': 1,
                'is_closed': False
            })

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


def update_today_data(asset_obj: Asset) -> object:
    share_obj = asset_obj.get_related_object()

    # In minutes
    STANDARD_MOEX_LAG = 16
    UPDATE_TIME_MINUTES = 60 - STANDARD_MOEX_LAG
    EVENING_CUT_OFF = datetime.strptime(datetime.strftime(
        datetime.today(), '%Y-%m-%d 18:30:00'), '%Y-%m-%d %H:%M:%S')

    latest_day = AssetsHistoricalData.objects.filter(
        asset=asset_obj).order_by('-tradedate')[0]

    if latest_day.update_time:

        update_time_dt = datetime.strptime(
            datetime.strftime(latest_day.update_time, '%Y-%m-%d %H:%M:%S'),
            '%Y-%m-%d %H:%M:%S')

        # IF STOCK IS NOT ON EVENING SESSION AND UPDATE TIME LATER THAN
        # 18:30:00 TODAY => NO NEED TO UPDATE
        if not share_obj.eveningsession and \
                update_time_dt > EVENING_CUT_OFF:
            return share_obj

        # IF UPDATED RECENTLY => NO NEED TO UPDATE
        time_gap = get_time_gap(update_time_dt)

        if time_gap <= UPDATE_TIME_MINUTES:
            return share_obj

    group = asset_obj.group

    board = get_asset_board(asset_obj.type)

    print(group, 'group', 'board', board, asset_obj.group, asset_obj.type)
    last_price_data = get_current(share_obj.secid, board, group)

    today_dt = datetime.today().date()

    stock_today_price_data, _ = AssetsHistoricalData.objects.get_or_create(
        tradedate=today_dt, asset=asset_obj, defaults={
            'legalcloseprice': last_price_data[0],
            'is_closed': False,
            'update_time': last_price_data[1]
        })

    stock_today_price_data.legalcloseprice = last_price_data[0]
    stock_today_price_data.is_closed = False
    stock_today_price_data.update_time = last_price_data[1]

    stock_today_price_data.save()

    return share_obj


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

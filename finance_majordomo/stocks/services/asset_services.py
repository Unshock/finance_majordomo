from django.db.models import QuerySet

from common.utils.stocks import get_stock_board_history, get_stock_description
from finance_majordomo.dividends.utils import add_dividends_to_model, \
    get_stock_dividends
from finance_majordomo.stocks.models import Asset, Stock, Bond, AssetOfPortfolio
from finance_majordomo.stocks.utils import add_share_history_data_to_model, \
    add_bond_history_data_to_model
from finance_majordomo.stocks.views import get_normalized_asset_type
from finance_majordomo.users.models import User


def add_asset(stock_description: dict) -> Stock:

    secid = stock_description.get('SECID')
    isin = stock_description.get('ISIN')

    name = stock_description.get('SHORTNAME')
    latname = stock_description.get('LATNAME')

    currency = 'RUR' if stock_description.get(
        'FACEUNIT') == 'SUR' else stock_description.get('FACEUNIT')
    issuedate = stock_description.get('ISSUEDATE')

    isqualifiedinvestors = True if \
        stock_description.get('ISQUALIFIEDINVESTORS') == '1' else False
    morningsession = True if \
        stock_description.get('MORNINGSESSION') == '1' else False
    eveningsession = True if \
        stock_description.get('EVENINGSESSION') == '1' else False

    type = stock_description.get('TYPE')
    typename = stock_description.get('TYPENAME')

    group = stock_description.get('GROUP')
    groupname = stock_description.get('GROUPNAME')

    asset_type = get_normalized_asset_type(type)

    check_list = [secid, name, isin,
                  currency, latname, isqualifiedinvestors,
                  issuedate, morningsession, eveningsession,
                  typename, group, type, groupname]

    if None in check_list:
        print("SOMETHING HAVE NOT BEEN LOADED - GOT NONE")

    # Ищем инфу о ценах акции за весь период чтобы записать в JSONField

    stock_board_history = get_stock_board_history(secid)

    stock_obj = Stock.objects.create(
        asset_type=asset_type,

        secid=secid,
        name=name,
        isin=isin,
        currency=currency,
        latname=latname,
        isqualifiedinvestors=isqualifiedinvestors,
        issuedate=issuedate,
        morningsession=morningsession,
        eveningsession=eveningsession,
        typename=typename,
        group=group,
        type=type,
        groupname=groupname,
        #stock_data=json_stock_board_data,
    )


    try:
        add_share_history_data_to_model(stock_obj, stock_board_history)

    except Exception('HISTORY PROBLEM'):
        pass

    # add dividend for stock
    try:
        dividends_dict = get_stock_dividends(stock_obj)
        add_dividends_to_model(stock_obj, dividends_dict)

    except Exception('something went wrong while download divs'):
        pass

    return stock_obj


def add_bond(stock_description: dict) -> Bond:
    secid = stock_description.get('SECID')
    isin = stock_description.get('ISIN')

    name = stock_description.get('SHORTNAME')
    latname = stock_description.get('LATNAME')

    currency = 'RUR' if stock_description.get(
        'FACEUNIT') == 'SUR' else stock_description.get('FACEUNIT')
    issuedate = stock_description.get('ISSUEDATE')

    isqualifiedinvestors = True if \
        stock_description.get('ISQUALIFIEDINVESTORS') == '1' else False
    morningsession = True if \
        stock_description.get('MORNINGSESSION') == '1' else False
    eveningsession = True if \
        stock_description.get('EVENINGSESSION') == '1' else False

    type = stock_description.get('TYPE')
    typename = stock_description.get('TYPENAME')

    group = stock_description.get('GROUP')
    groupname = stock_description.get('GROUPNAME')

    asset_type = get_normalized_asset_type(type)

    startdatemoex = stock_description.get('STARTDATEMOEX')
    buybackdate = stock_description.get('BUYBACKDATE')
    matdate = stock_description.get('MATDATE')
    couponfrequency = stock_description.get('COUPONFREQUENCY')
    couponpercent = stock_description.get('COUPONPERCENT')
    couponvalue = stock_description.get('COUPONVALUE')
    days_to_redemption = stock_description.get('DAYSTOREDEMPTION')



    check_list = [secid, name, isin,
                  currency, latname, isqualifiedinvestors,
                  issuedate, morningsession, eveningsession,
                  typename, group, type, groupname]

    boards_dict = {
        'ofz_bond': 'TQOB',
        'corporate_bond': 'TQCB',
        'exchange_bond': 'TQCB'
    }

    board = boards_dict.get(type)

    if None in check_list:
        print("SOMETHING HAVE NOT BEEN LOADED - GOT NONE")

    # Ищем инфу о ценах акции за весь период чтобы записать в JSONField
    print(secid)
    print(type, board)
    stock_board_history = get_stock_board_history(secid, market='bonds',
                                                  board=board)

    bond_obj = Bond.objects.create(
        asset_type=asset_type,

        secid=secid,
        name=name,
        isin=isin,
        currency=currency,
        latname=latname,
        isqualifiedinvestors=isqualifiedinvestors,
        issuedate=issuedate,
        morningsession=morningsession,
        eveningsession=eveningsession,
        typename=typename,
        group=group,
        type=type,
        groupname=groupname,

        startdatemoex=startdatemoex,
        buybackdate=buybackdate,
        matdate=matdate,
        couponfrequency=couponfrequency,
        couponpercent=couponpercent,
        couponvalue=couponvalue,
        days_to_redemption=days_to_redemption


    )

    try:
        add_bond_history_data_to_model(bond_obj, stock_board_history)

    except Exception('HISTORY PROBLEM'):
        pass

    # # add dividend for stock
    # try:
    #     dividends_dict = get_stock_dividends(stock_obj)
    #     add_dividends_to_model(stock_obj, dividends_dict)
    # 
    # except Exception('something went wrong while download divs'):
    #     pass

    return bond_obj


def create_asset_obj(asset_description: dict) -> Asset:
    asset_type = asset_description.get('GROUP')

    if asset_type == 'stock_shares':
        return add_asset(asset_description)

    elif asset_type == 'stock_bonds':
        return add_bond(asset_description)

    else:
        raise Exception('type is incorrect')


def get_all_assets_of_user(user: User) -> QuerySet:

    assets_of_user = Asset.objects.none()

    portfolios_of_user = user.portfolio_set.all()

    for portfolio in portfolios_of_user:

        portfolio_assets = Asset.objects.filter(
            id__in=portfolio.assetofportfolio_set.values_list('asset'))

        assets_of_user |= portfolio_assets

    return assets_of_user


def add_asset_to_portfolio(asset, portfolio):

    AssetOfPortfolio.objects.get_or_create(
        asset=asset,
        portfolio=portfolio
    )


def get_or_create_asset_obj(asset_secid: str) -> Asset:

    try:
        asset_obj = Asset.objects.get(secid=asset_secid)

    except Asset.DoesNotExist:
        asset_description = get_stock_description(asset_secid)
        asset_obj = create_asset_obj(asset_description)

    return asset_obj

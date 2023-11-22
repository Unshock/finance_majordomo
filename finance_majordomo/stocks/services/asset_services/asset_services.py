from decimal import Decimal

from django.db.models import QuerySet

from common.utils.stocks import get_bond_coupon_history
from finance_majordomo.stocks.models.currency import CurrencyRate

from finance_majordomo.stocks.models.asset import Asset, Stock, Bond, \
    AssetOfPortfolio, AssetsHistoricalData

from finance_majordomo.stocks.utils.assets_utils import add_share_history_data_to_model, \
    add_bond_history_data_to_model, get_asset_history_data, get_asset_board
#from finance_majordomo.stocks.views import get_normalized_asset_type
from finance_majordomo.users.models import User

# 
# def create_base_asset(asset_description: dict) -> Asset:
#     secid = asset_description.get('SECID')
#     isin = asset_description.get('ISIN')
# 
#     name = asset_description.get('SHORTNAME')
#     latname = asset_description.get('LATNAME')
# 
#     currency = 'RUR' if asset_description.get(
#         'FACEUNIT') == 'SUR' else asset_description.get('FACEUNIT')
#     issuedate = asset_description.get('ISSUEDATE')
# 
#     isqualifiedinvestors = True if \
#         asset_description.get('ISQUALIFIEDINVESTORS') == '1' else False
#     morningsession = True if \
#         asset_description.get('MORNINGSESSION') == '1' else False
#     eveningsession = True if \
#         asset_description.get('EVENINGSESSION') == '1' else False
# 
#     type = asset_description.get('TYPE')
#     typename = asset_description.get('TYPENAME')
# 
#     group = asset_description.get('GROUP')
#     groupname = asset_description.get('GROUPNAME')
#     primary_boardid = asset_description.get('primary_boardid')
#     
# 
#     asset_type = get_normalized_asset_type(type)
# 
#     check_list = [secid, name, isin,
#                   currency, latname, isqualifiedinvestors,
#                   issuedate, morningsession, eveningsession,
#                   typename, group, type, groupname]
# 
#     if None in check_list:
#         print("SOMETHING HAVE NOT BEEN LOADED - GOT NONE")
# 
#     asset_obj = Asset.objects.create(
#         asset_type=asset_type,
# 
#         secid=secid,
#         name=name,
#         isin=isin,
#         currency=currency,
#         latname=latname,
#         isqualifiedinvestors=isqualifiedinvestors,
#         issuedate=issuedate,
#         morningsession=morningsession,
#         eveningsession=eveningsession,
#         typename=typename,
#         group=group,
#         type=type,
#         groupname=groupname,
#         primary_boardid=primary_boardid
#         #stock_data=json_stock_board_data,
#     )
#     
#     print("ASSET OBJ", asset_obj)
#     
#     return asset_obj


# def add_asset(stock_description: dict) -> Stock:
# 
#     secid = stock_description.get('SECID')
#     isin = stock_description.get('ISIN')
# 
#     name = stock_description.get('SHORTNAME')
#     latname = stock_description.get('LATNAME')
# 
#     currency = 'RUR' if stock_description.get(
#         'FACEUNIT') == 'SUR' else stock_description.get('FACEUNIT')
#     issuedate = stock_description.get('ISSUEDATE')
# 
#     isqualifiedinvestors = True if \
#         stock_description.get('ISQUALIFIEDINVESTORS') == '1' else False
#     morningsession = True if \
#         stock_description.get('MORNINGSESSION') == '1' else False
#     eveningsession = True if \
#         stock_description.get('EVENINGSESSION') == '1' else False
# 
#     type = stock_description.get('TYPE')
#     typename = stock_description.get('TYPENAME')
# 
#     group = stock_description.get('GROUP')
#     groupname = stock_description.get('GROUPNAME')
#     primary_boardid = stock_description.get('primary_boardid')
# 
#     asset_type = get_normalized_asset_type(type)
# 
#     check_list = [secid, name, isin,
#                   currency, latname, isqualifiedinvestors,
#                   issuedate, morningsession, eveningsession,
#                   typename, group, type, groupname]
# 
#     if None in check_list:
#         print("SOMETHING HAVE NOT BEEN LOADED - GOT NONE")
#         
#     print("AAAAAAAAAAAAAAAAAAAAAAAAAAAA'", issuedate)
# 
#     # Ищем инфу о ценах акции за весь период чтобы записать в JSONField
# 
#     stock_obj = Stock.objects.create(
#         asset_type=asset_type,
# 
#         secid=secid,
#         name=name,
#         isin=isin,
#         currency=currency,
#         latname=latname,
#         isqualifiedinvestors=isqualifiedinvestors,
#         issuedate=issuedate,
#         morningsession=morningsession,
#         eveningsession=eveningsession,
#         typename=typename,
#         group=group,
#         type=type,
#         groupname=groupname,
#         primary_boardid=primary_boardid
#         #stock_data=json_stock_board_data,
#     )
#     
#     print(stock_obj, '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
# 
#     asset_history_data = get_asset_history_data(stock_obj)
#     
#     try:
#         add_share_history_data_to_model(stock_obj, asset_history_data)
# 
#     except Exception as e:
#         print('History problev', e)
#         pass
# 
#     # add dividend for stock
#     try:
#         dividends_dict = get_stock_dividends(stock_obj)
#         add_dividends_to_model(stock_obj, dividends_dict)
# 
#     except Exception('something went wrong while download divs'):
#         pass
# 
#     return stock_obj



# def add_bond(stock_description: dict) -> Bond:
#     secid = stock_description.get('SECID')
#     isin = stock_description.get('ISIN')
# 
#     name = stock_description.get('SHORTNAME')
#     latname = stock_description.get('LATNAME')
# 
#     currency = 'RUR' if stock_description.get(
#         'FACEUNIT') == 'SUR' else stock_description.get('FACEUNIT')
#     issuedate = stock_description.get('ISSUEDATE')
# 
#     isqualifiedinvestors = True if \
#         stock_description.get('ISQUALIFIEDINVESTORS') == '1' else False
#     morningsession = True if \
#         stock_description.get('MORNINGSESSION') == '1' else False
#     eveningsession = True if \
#         stock_description.get('EVENINGSESSION') == '1' else False
# 
#     type = stock_description.get('TYPE')
#     typename = stock_description.get('TYPENAME')
# 
#     group = stock_description.get('GROUP')
#     groupname = stock_description.get('GROUPNAME')
#     primary_boardid = stock_description.get('primary_boardid')
# 
#     asset_type = get_normalized_asset_type(type)
# 
#     startdatemoex = stock_description.get('STARTDATEMOEX')
#     buybackdate = stock_description.get('BUYBACKDATE')
#     matdate = stock_description.get('MATDATE')
#     couponfrequency = stock_description.get('COUPONFREQUENCY')
#     couponpercent = stock_description.get('COUPONPERCENT')
#     couponvalue = stock_description.get('COUPONVALUE')
#     days_to_redemption = stock_description.get('DAYSTOREDEMPTION')
#     face_value = stock_description.get('FACEVALUE')
#     
#     print(face_value, '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
# 
# 
# 
#     check_list = [secid, name, isin,
#                   currency, latname, isqualifiedinvestors,
#                   issuedate, morningsession, eveningsession,
#                   typename, group, type, groupname]
# 
#     board = get_asset_board(type)
# 
#     if None in check_list:
#         print("SOMETHING HAVE NOT BEEN LOADED - GOT NONE")
# 
#     # Ищем инфу о ценах акции за весь период чтобы записать в JSONField
# 
#     
#     print(stock_description)
# 
#     bond_obj = Bond.objects.create(
#         asset_type=asset_type,
# 
#         secid=secid,
#         name=name,
#         isin=isin,
#         currency=currency,
#         latname=latname,
#         isqualifiedinvestors=isqualifiedinvestors,
#         issuedate=issuedate,
#         morningsession=morningsession,
#         eveningsession=eveningsession,
#         typename=typename,
#         group=group,
#         type=type,
#         groupname=groupname,
#         primary_boardid=primary_boardid,
# 
#         startdatemoex=startdatemoex,
#         buybackdate=buybackdate,
#         matdate=matdate,
#         couponfrequency=couponfrequency,
#         couponpercent=couponpercent,
#         couponvalue=couponvalue,
#         days_to_redemption=days_to_redemption,
#         face_value=face_value
# 
# 
#     )
# 
#     #print(secid)
#     #print(type, board)
#     asset_history_data = get_asset_history_data(bond_obj)
# 
#     try:
#         add_bond_history_data_to_model(bond_obj, asset_history_data)
# 
#     except Exception('HISTORY PROBLEM'):
#         pass
# 
#     # add dividend for stock
#     try:
#         dividends_dict = get_bond_coupon_history(bond_obj.secid)
#         add_dividends_to_model(bond_obj, dividends_dict)
# 
#     except Exception:
#         raise Exception('something went wrong while download coupons')
# 
#     return bond_obj


# def create_asset_obj(asset_description: dict) -> Asset:
#     asset_type = asset_description.get('GROUP')
# 
#     if asset_type == 'stock_shares':
#         return add_asset(asset_description)
# 
#     elif asset_type == 'stock_bonds':
#         return add_bond(asset_description)
# 
#     else:
#         raise Exception('type is incorrect')

def add_asset_to_portfolio(asset, portfolio):

    AssetOfPortfolio.objects.get_or_create(
        asset=asset,
        portfolio=portfolio
    )

def get_currency_rate(currency: str = None):
    if currency and currency.lower() == 'usd':
        currency_rate = CurrencyRate.objects.last().price_usd
    else:
        currency_rate = Decimal('1')

    return currency_rate


def get_current_asset_price_per_asset(asset: Asset, currency: str) -> Decimal:

    currency_rate = get_currency_rate(currency)

    last_date_price = AssetsHistoricalData.objects.filter(
        asset=asset).order_by('-tradedate')[0].legalcloseprice

    current_price = last_date_price / currency_rate

    if asset.group == 'stock_bonds':
        bond = asset.get_related_object()
        current_price = current_price * bond.face_value / 100

    return Decimal(current_price)

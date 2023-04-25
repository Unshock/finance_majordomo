import json
import datetime
import requests
from urllib3.util.retry import Retry

import apimoex



def validate_ticker(ticker: str):

    if not ticker:
        return None

    request_url = ('https://iss.moex.com/iss/engines/stock/'
                   'markets/shares/boards/TQBR/securities.json')
    arguments = {'securities.columns': ('SECID,'
                                        'REGNUMBER,'
                                        'LOTSIZE,'
                                        'SHORTNAME')}
    with requests.Session() as session:
        iss = apimoex.ISSClient(session, request_url, arguments)
        data = iss.get()
        #print(data)
        try:
            ticker_data = next(x for x in data['securities'] if x["SECID"] == ticker.upper())
            ticker_data = {'ticker': ticker_data['SECID'],
                          'shortname': ticker_data['SHORTNAME']}

        except StopIteration:
            ticker_data = None
        #print(ticker_data)
        return ticker_data




def get_stock_board_history(ticker: str, start_date:str=None):
    """
    :param ticker: ticker for MOEX API
    :param start_date: the earliest trading date from which information will be received to current date
    :return: list of dicts with data for every day from start_day or first historic day if start_day is None
    """

    with requests.Session() as session:
        print(f"ZAPROS данных по тикеру {ticker} начиная с {start_date}")

        data = apimoex.get_board_history(session, ticker.upper(), start=start_date)

        if data:
            return data#print('данные получены')
        else:
            print('ДАННЫЕ НЕ ПОЛУЧЕНЫ!!!!!!!!!')



def get_stock_current_price(ticker: str):

    #тут нужно поправить для акций не торгующихся в вечернюю сессию
    TIME_GAP_MINUTES = 600

    offset = datetime.timezone(datetime.timedelta(hours=3))

    current_time = datetime.datetime.now(offset)
    request_time = current_time - datetime.timedelta(minutes=TIME_GAP_MINUTES)

    print(current_time, request_time)

    with requests.Session() as session:
        print(f'ZAPROS na poluchenie last_price of {ticker.upper()} poshel')
        data = apimoex.get_board_candles(session, ticker.upper(), start=str(request_time), interval=1)
        #data = apimoex.find_security_description(session, ticker.upper())
        #print('data', '\n'.join(str(d) for d in data))
        if data:
            lastest_data = data[-1]
            last_price = lastest_data.get('close')
            actual_time = lastest_data.get('begin')

            #print('last price:', last_price, 'actual_time:', actual_time)

            if last_price and actual_time:
               return last_price, actual_time
            else:
               raise ValueError(f'Could not get data for {ticker} in {get_stock_current_price}')


        raise ValueError(f'Could not get data for {ticker} in {get_stock_current_price}')


def get_stock_description(ticker: str):
    with requests.Session() as session:
        data = apimoex.find_security_description(session, ticker.upper())
        #print(data)
        result_data = {}
        for elem in data:
            result_data[elem['name']] = elem['value']
        return result_data

def get_security(security_info: str):
    with requests.Session() as session:
        data = apimoex.find_securities(session, security_info.upper(), columns=('secid', 'regnumber', 'name', 'type', 'group'))
        #print(data)
        return data


# a = get_security('SU26222RMFS8, RU000A0JXQF2')
# print(len(a))
# for el in a[:10]:
#    print(el['secid'], el['name'], el.get('type'), el.get('group'))
#
# b = get_stock_description('SBER')
# for key, value in b.items():
#    print(key, value)


def make_json_trade_info_dict(data: list):
    trade_info = {
        trade_day['TRADEDATE']: {
            'BOARDID': trade_day['BOARDID'],
            'CLOSE': trade_day['CLOSE'],
            'VOLUME': trade_day['VOLUME'],
            'VALUE': trade_day['VALUE']
        } for trade_day in data}

    return json.dumps({"TRADEINFO": trade_info})

def make_json_last_price_dict(last_price, actual_time):
    today = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')

    #print(actual_time)

    trade_info = {
        today: {
            'LAST': last_price,
            'UPDATE_TIME': actual_time,
        }}

    return json.dumps({"TRADEINFO": trade_info})


def get_date_status(date):
    url = f'https://isdayoff.ru/{date}'

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    result = session.get(url).text

    if result == '0':
        return 'Working'
    if result == '1':
        return 'Nonworking'
    raise ConnectionError('Response is not valid')

import json

import requests
import datetime
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
            print('данные получены')
        else:
            print('ДАННЫЕ НЕ ПОЛУЧЕНЫ!!!!!!!!!')

        return data

def get_stock_current_price(ticker: str):

    TIME_GAP_MINUTES = 1000

    offset = datetime.timezone(datetime.timedelta(hours=3))

    current_time = datetime.datetime.now(offset)
    request_time = current_time - datetime.timedelta(minutes=TIME_GAP_MINUTES)

    #print(current_time, request_time)

    with requests.Session() as session:
        print(f'ZAPROS na poluchenie last_price of {ticker.upper()} poshel')
        data = apimoex.get_board_candles(session, ticker.upper(), start=str(request_time), interval=1)
        #data = apimoex.find_security_description(session, ticker.upper())
        #print('data', '\n'.join(str(d) for d in data))
        if data:
            lastest_data = data[-1]
            last_price = lastest_data.get('close')
            actual_time = lastest_data.get('begin')

            if last_price and actual_time:
               return last_price, actual_time
            else:
               raise ValueError(f'Could not get data for {ticker} in {get_stock_current_price}')


        raise ValueError(f'Could not get data for {ticker} in {get_stock_current_price}')


#print(get_stock_current_price('lsrg'))
#print(get_stock_current_price('sber'))


def is_admitted_for_sessions(ticker: str):
    with requests.Session() as session:
        print(f'ZAPROS na poluchenie admitted for sessions of {ticker.upper()} poshel')
        #data = apimoex.get_board_candles(session, ticker.upper(), start=request_time, interval=1)
        data = apimoex.find_security_description(session, ticker.upper())
        print('data', '\n'.join(str(d) for d in data))

        admitted_for_morning = False
        admitted_for_evening = False

        for parameter in data:
            if parameter['name'] == 'MORNINGSESSION' and parameter['value'] == '1':
                admitted_for_morning = True
            if parameter['name'] == 'EVENINGSESSION' and parameter['value'] == '1':
                admitted_for_evening = True

        return {'admitted_for_morning_session': admitted_for_morning,
                'admitted_for_evening_session': admitted_for_evening}

def get_stock_description(ticker: str):
    with requests.Session() as session:
        #print(f'ZAPROS na poluchenie stock description of {ticker.upper()} poshel')
        #data = apimoex.get_board_candles(session, ticker.upper(), start=request_time, interval=1)
        data = apimoex.find_security_description(session, ticker.upper())
        #print('data', '\n'.join(str(d) for d in data))

        result_data = {}
        for elem in data:
            result_data[elem['name']] = elem['value']
        return result_data

#is_admitted_for_sessions('posi')
#a = get_stock_description('sber')
#print(a)


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


# stock_board_history = get_stock_board_history('sber', '2023-03-18')
# stock_board_data_json = json.loads(make_json_trade_info_dict(stock_board_history))
#
# last_price, actual = get_stock_current_price('sber')
# data = json.loads(make_json_last_price_dict(last_price, actual))
#
# print(stock_board_data_json)
# print(data)
#
# res = stock_board_data_json['TRADEINFO'].update(data['TRADEINFO'])
#
# print(stock_board_data_json)

# g = {'TRADEINFO': {'2023-03-20': {'BOARDID': 'TQBR', 'CLOSE': 203.73, 'VOLUME': 156714250, 'VALUE': 31309861829}, '2023-03-21': {'BOARDID': 'TQBR', 'CLOSE': 203.32, 'VOLUME': 122583960, 'VALUE': 25112540900.7}, '2023-03-22': {'LAST': 203.88, 'ACTUAL': '2023-03-22 21:03:00'}}}
# u = {'TRADEINFO': {'2023-03-20': {'BOARDID': 'z', 'CLOSE': 0.0, 'VOLUME': 0, 'VALUE': 0}, '2023-03-22': {'BOARDID': 'TQBR', 'CLOSE': 203.73, 'VOLUME': 156714250, 'VALUE': 31309861829}}}
#
# print(g)
# print(u)
#
# g['TRADEINFO'].update(u['TRADEINFO'])

def get_date_status(date):
    url = f'https://isdayoff.ru/{date}'
    result = requests.get(url).text
    if result == '0':
        return 'Working'
    if result == '1':
        return 'Nonworking'
    raise ConnectionError('Response is not valid')


# ticker = 'sber'
# date = '2023-02-17'
#aaa = [{"BOARDID": "TQBR", "TRADEDATE": "2013-03-25", "CLOSE": 98.79, "VOLUME": 593680, "VALUE": 59340002.8}, {"BOARDID": "TQBR", "TRADEDATE": "2013-03-26", "CLOSE": 97.2, "VOLUME": 1283550, "VALUE": 126030358.8}, {"BOARDID": "TQBR", "TRADEDATE": "2013-03-27", "CLOSE": 96.75, "VOLUME": 1261950, "VALUE": 121835900.2}]
#aaa = get_stock_board_history(ticker, date)
#print(aaa)



#validate_ticker(ticker)
#a = get_stock_board_history(ticker)
# res = {'trade_info': dict}
# jres = json.dumps(res)
# print(res)
# print(jres)

#res = requests.get(url)
#print(res.text)



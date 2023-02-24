import json

import requests
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
        return ticker_data




def get_stock_board_history(ticker: str, date:str=None):
    print('ticker', ticker, 'data: ', date)
    with requests.Session() as session:
        data = apimoex.get_board_history(session, ticker.upper(), start=date)
        return data

def make_json_trade_info_dict(data: list):
    trade_info = {
        trade_day['TRADEDATE']: {
            'BOARDID': trade_day['BOARDID'],
            'CLOSE': trade_day['CLOSE'],
            'VOLUME': trade_day['VOLUME'],
            'VALUE': trade_day['VALUE']
        } for trade_day in data}

    return json.dumps({"TRADEINFO": trade_info})


def get_date_status(date):
    url = f'https://isdayoff.ru/{date}'
    return requests.get(url).text

ticker = 'sber'
date = '2023-02-17'
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



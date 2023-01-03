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
        try:
            ticker_data = next(x for x in data['securities'] if x["SECID"] == ticker.upper())
        except StopIteration:
            ticker_data = None
        print(ticker_data)
        if not ticker_data:
            return None
        return {'ticker': ticker_data['SECID'],
                'shortname': ticker_data['SHORTNAME']}

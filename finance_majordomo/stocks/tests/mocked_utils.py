import json

from .conftest import make_get_stock_desc_lsng, make_get_stock_desc_lsngp, \
    make_get_stock_desc_tatn, make_get_stock_desc_tatnp


def mocked_get_stock_description(ticker: str):
    json_result_dict = {
        'LSNG': make_get_stock_desc_lsng,
        'LSNGP': make_get_stock_desc_lsngp,
        'TATN': make_get_stock_desc_tatn,
        'TATNP': make_get_stock_desc_tatnp,
    }

    print(222)
    print(ticker)
    json_result_path = json_result_dict.get(ticker.upper())()
    json_result = open(json_result_path)
    result = json.load(json_result)
    return result

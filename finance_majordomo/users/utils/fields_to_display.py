

FIELDS_TO_DISPLAY = [
    'ticker',
    'name',
    'currency',
    'quantity',
    'purchase_price',
    'current_price',
    'dividends_received',
    'money_result_without_divs',
    'money_result_with_divs',
    'percent_result',
    'rate_of_return',
]


def get_default_display_options():
    fields = dict()
    for field in FIELDS_TO_DISPLAY:
        fields[field] = True
    return fields
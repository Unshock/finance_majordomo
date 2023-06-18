import pytest
import os


FIXTURES_FOLDER = 'fixtures'



def make_get_stock_desc_lsng():
    json_file_path = os.path.join(os.path.dirname(__file__),
                                  FIXTURES_FOLDER,
                                  'get_stock_description_lsng.json')
    return json_file_path

def make_get_stock_desc_lsngp():
    json_file_path = os.path.join(os.path.dirname(__file__),
                                  FIXTURES_FOLDER,
                                  'get_stock_description_lsngp.json')
    return json_file_path

def make_get_stock_desc_tatn():
    json_file_path = os.path.join(os.path.dirname(__file__),
                                  FIXTURES_FOLDER,
                                  'get_stock_description_tatn.json')
    return json_file_path

def make_get_stock_desc_tatnp():
    json_file_path = os.path.join(os.path.dirname(__file__),
                                  FIXTURES_FOLDER,
                                  'get_stock_description_tatnp.json')
    return json_file_path
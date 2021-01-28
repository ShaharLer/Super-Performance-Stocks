import os.path
import time
from concurrent.futures import ThreadPoolExecutor

from background_task import background
from django.utils import timezone

from stocks_tracker import models
from .marketwatch_financial_stock import MarketwatchFinancialStock

global_stocks_dict = {}  # The keys are stock symbols and the values are: net-income, eps and sales growths arrays.
NET_INCOME_KEY = 'net_income'
EPS_KEY = 'eps'
SALES_KEY = 'sales'
DATA_DELIMITERS = ['%']


def set_stock_data(stock, stock_data, duration):
    if duration == 'q':
        stock.net_income_growth_q = stock_data[NET_INCOME_KEY]
        stock.eps_growth_q = stock_data[EPS_KEY]
        stock.sales_growth_q = stock_data[SALES_KEY]
        stock.is_scrapper_succeeded_q = True
    else:
        stock.net_income_growth_y = stock_data[NET_INCOME_KEY]
        stock.eps_growth_y = stock_data[EPS_KEY]
        stock.sales_growth_y = stock_data[SALES_KEY]
        stock.is_scrapper_succeeded_y = True


def reset_stock_data(stock,duration):
    if duration == 'q':
        stock.net_income_growth_q = stock.eps_growth_q = stock.sales_growth_q = None
    else:
        stock.net_income_growth_y = stock.eps_growth_y = stock.sales_growth_y = None


def update_new_stock(stock, stock_symbol, stock_name):
    stock.symbol = stock_symbol
    stock.name = stock_name


def reset_existed_stock_attributes(stock):
    stock.pivot = stock.is_accelerated = stock.is_eps_growth = stock.is_technically_valid = stock.is_breakout = \
        stock.price_to_sell = None


def update_stock_fields_after_scrapper(stock, stock_symbol, stock_name, stock_data, duration):
    reset_stock_data(stock, duration)
    stock.last_scrapper_update = timezone.now()

    if not stock.symbol:
        update_new_stock(stock, stock_symbol, stock_name)
    else:
        reset_existed_stock_attributes(stock)

    if stock_data is not None:
        set_stock_data(stock, stock_data, duration)
    else:
        stock.is_scrapper_succeeded = False


def get_stock(symbol):
    if len(models.Stock.objects.filter(symbol=symbol)) == 0:  # stock does not exist yet
        return models.Stock()
    else:
        return models.Stock.objects.get(symbol=symbol)


def write_to_db(stock_key, stock_data, duration):
    stock_symbol = stock_key.split()[0]
    try:
        stock_name = stock_key.split()[1]
        stock = get_stock(stock_symbol)
        update_stock_fields_after_scrapper(stock, stock_symbol, stock_name, stock_data, duration)
        stock.save()
    except Exception as e:
        print(f'Failed to save stock {stock_symbol} in the DB after scrapper run: {str(e)}')


def write_stocks_to_db(duration):
    for stock_key in global_stocks_dict:
        write_to_db(stock_key, global_stocks_dict[stock_key], duration)


def get_data_as_number(data_as_string):
    try:
        data_as_string = data_as_string.replace(',','')
        for delimiter in DATA_DELIMITERS:
            data_as_string = data_as_string.replace(delimiter, '')
        return float(data_as_string)
    except ValueError:
        return None


def calc_stock_data_by_key(stock, stock_data_key, stock_data_dict):
    data_list = []
    if stock_data_key == NET_INCOME_KEY:
        data_list = stock.get_net_income_growth_array()
    elif stock_data_key == EPS_KEY:
        data_list = stock.get_eps_growth_array()
    elif stock_data_key == SALES_KEY:
        data_list = stock.get_sales_growth_array()

    data_list = [get_data_as_number(data) for data in data_list]
    stock_data_dict[stock_data_key] = data_list if None not in data_list else []


def get_stock_data(stock_symbol,duration):

    stock = MarketwatchFinancialStock(stock_symbol,duration)
    stock_data = {}
    calc_stock_data_by_key(stock, NET_INCOME_KEY, stock_data)
    calc_stock_data_by_key(stock, EPS_KEY, stock_data)
    calc_stock_data_by_key(stock, SALES_KEY, stock_data)
    return stock_data


def run_stock_scrapper(stock_key,duration):
    try:
        stock_data = get_stock_data(stock_key.split()[0],duration)
        global_stocks_dict[stock_key] = stock_data

    except:
        global_stocks_dict[stock_key] = None


def iterate_over_all_stock(all_stocks,duration):
    global global_stocks_dict
    start = time.time()
    maximum_threads = 200
    timeout_between_threads_creation = 0.02
    pool = ThreadPoolExecutor(max_workers=maximum_threads)

    for stock_key in all_stocks:
        try:
            stock_symbol = stock_key.split()[0]
            print(stock_symbol)  # print stock symbol
            pool.submit(run_stock_scrapper, stock_key,duration)
            time.sleep(timeout_between_threads_creation)
        except:
            pass

    pool.shutdown(wait=True)
    end = time.time()
    print(f'Running all threads took {round(end - start, 2)} seconds')


def get_all_stocks_list():
    all_stocks_file = 'all_stocks.txt'
    all_stocks_file_full_path = f'{os.path.dirname(os.path.realpath(__file__))}\\{all_stocks_file}'
    if not os.path.exists(all_stocks_file_full_path):
        return None

    stock_name_invalid_suffix = ['-', '.']
    stocks_list = []

    with open(all_stocks_file_full_path, 'r') as all_stocks:
        for stock_line in all_stocks:
            stock_symbol_and_name = stock_line.split()
            if len(stock_symbol_and_name) == 2:
                stock_symbol = stock_symbol_and_name[0]
                stock_name = stock_symbol_and_name[1]
                if stock_name[-1] in stock_name_invalid_suffix:
                    stock_name = stock_name[:-1]
                stocks_list.append(f'{stock_symbol} {stock_name}')

    return stocks_list


@background()
def marketwatch_scrapper_main(duration):
    print(f'Started marketwatch_scrapper_main with duration: {duration}')
    all_stocks_list = get_all_stocks_list()
    iterate_over_all_stock(all_stocks_list,duration)
    write_stocks_to_db(duration)
    print(f'Finished marketwatch_scrapper_main with duration: {duration}')

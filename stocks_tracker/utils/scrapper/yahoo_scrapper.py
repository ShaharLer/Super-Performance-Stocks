import os.path
import time
from concurrent.futures import ThreadPoolExecutor
from background_task import background
from django.utils import timezone
from stocks_tracker.models import Stock
from .yahoo_financial_stock import YahooFinancialStock

global_stocks_dict = {}  # The keys are stock symbols and the values are: YahooFinancialStock objects.



def set_stock_data(stock, yahoo_stock_object):
    stock.target_avg_sales = yahoo_stock_object.target_avg_sales
    stock.target_avg_eps = yahoo_stock_object.target_avg_eps
    stock.target_sales_growth = yahoo_stock_object.target_sales_growth
    stock.is_yahoo_scrapper_succeeded = True


def reset_stock_data(stock):
    stock.target_sales_growth = stock.target_avg_eps = stock.target_avg_sales = None


def update_new_stock(stock, stock_symbol, stock_name):
    stock.symbol = stock_symbol
    stock.name = stock_name


def reset_existed_stock_attributes(stock):
    stock.pivot = stock.is_accelerated = stock.is_eps_growth = stock.is_technically_valid = stock.is_breakout = None


def update_stock_fields_after_scrapper(stock, stock_symbol, stock_name, yahoo_stock_object):
    reset_stock_data(stock)
    stock.last_scrapper_update = timezone.now()

    if not stock.symbol:
        update_new_stock(stock, stock_symbol, stock_name)
    else:
        reset_existed_stock_attributes(stock)

    if yahoo_stock_object is not None:
        set_stock_data(stock, yahoo_stock_object)
    else:
        stock.is_scrapper_succeeded = False


def get_stock(symbol):
    stock = Stock() if len(Stock.objects.filter(symbol=symbol)) == 0 else Stock.objects.get(symbol=symbol)
    return stock


def write_to_db(stock_key, yahoo_stock_object):
    stock_symbol = stock_key.split()[0]
    try:
        stock_name = stock_key.split()[1]
        stock = get_stock(stock_symbol)
        update_stock_fields_after_scrapper(stock, stock_symbol, stock_name, yahoo_stock_object)
        stock.save()
    except Exception as e:
        print(f'Failed to save stock {stock_symbol} in the DB after scrapper run: {str(e)}')


def write_stocks_to_db():
    for stock_key in global_stocks_dict:
        write_to_db(stock_key, global_stocks_dict[stock_key])


def get_data_as_number(data_as_string):
    try:
        for delimiter in DATA_DELIMITERS:
            data_as_string = data_as_string.replace(delimiter, '')
        return float(data_as_string)
    except ValueError:
        return None


def get_yahoo_stock_object(stock_symbol):
    stock = YahooFinancialStock(stock_symbol)
    return stock


def run_yahoo_stock_scrapper(stock_key):
    try:
        yahoo_stock_object = get_yahoo_stock_object(stock_key.split()[0])
        global_stocks_dict[stock_key] = yahoo_stock_object
    except:
        global_stocks_dict[stock_key] = None


def iterate_over_all_stock(all_stocks):
    global global_stocks_dict
    start = time.time()
    maximum_threads = 200
    timeout_between_threads_creation = 0.02
    pool = ThreadPoolExecutor(max_workers=maximum_threads)

    for stock_key in all_stocks:
        try:
            stock_symbol = stock_key.split()[0]
            print(stock_symbol)  # print stock symbol
            pool.submit(run_yahoo_stock_scrapper, stock_key)
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


def yahoo_scrapper_main():
    print('Started yahoo_scrapper_main')
    all_stocks_list = get_all_stocks_list()
    iterate_over_all_stock(all_stocks_list)
    write_stocks_to_db()
    print('Finished yahoo_scrapper_main')
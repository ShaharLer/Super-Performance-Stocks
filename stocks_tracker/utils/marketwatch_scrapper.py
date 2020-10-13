import os.path
import time
from concurrent.futures import ThreadPoolExecutor
from stocks_tracker.models import Stock
from .marketwatch_stock_financials_class import marketwatch_stock_financials_class


global_stocks_dict = {}  # The keys are stock symbols and the values are: net-income, eps and sales growths arrays.
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ALL_STOCKS_FILE = 'all_stocks.txt'
NET_INCOME_KEY = 'net_income'
EPS_KEY = 'eps'
SALES_KEY = 'sales'
DATA_DELIMITERS = ['%']


def write_to_db(stock_key, stock_data):
    try:
        stock_symbol = stock_key.split()[0]
        stock = Stock() if len(Stock.objects.filter(symbol=stock_symbol)) == 0 else Stock.objects.get(symbol=stock_symbol)
        stock.symbol = stock_symbol
        stock.name = stock_key.split()[1]
        if stock_data is not None:
            stock.net_income_growth = stock_data[NET_INCOME_KEY]
            stock.eps_growth = stock_data[EPS_KEY]
            stock.sales_growth = stock_data[SALES_KEY]
            stock.is_scrapper_succeeded = True
        else:
            stock.is_scrapper_succeeded = False
        stock.save()
    except:
        print(f'Failed to write {stock_key} to DB')


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


def calc_stock_data_by_key(stock, stock_data_key, stock_data_dict):
    data_list = []
    if stock_data_key == NET_INCOME_KEY:
        data_list = stock.get_q_net_income_growth_array()
    elif stock_data_key == EPS_KEY:
        data_list = stock.get_q_eps_growth_array()
    elif stock_data_key == SALES_KEY:
        data_list = stock.get_q_sales_growth_array()

    data_list = [get_data_as_number(data) for data in data_list]
    stock_data_dict[stock_data_key] = data_list if None not in data_list else []


def get_stock_data(stock_symbol):
    stock = marketwatch_stock_financials_class(stock_symbol)
    stock_data = {}
    calc_stock_data_by_key(stock, NET_INCOME_KEY, stock_data)
    calc_stock_data_by_key(stock, EPS_KEY, stock_data)
    calc_stock_data_by_key(stock, SALES_KEY, stock_data)
    return stock_data


def run_stock_scrapper(stock_key):
    global global_stocks_dict
    try:
        stock_data = get_stock_data(stock_key.split()[0])
        global_stocks_dict[stock_key] = stock_data
    except:
        global_stocks_dict[stock_key] = None


def iterate_over_all_stock():
    start = time.time()
    maximum_threads = 200
    timeout_between_threads_creation = 0.02
    stock_name_invalid_suffix = {'-', '.'}
    all_stock_file_path = f'{BASE_DIR}\\{ALL_STOCKS_FILE}'
    if not os.path.exists(all_stock_file_path):
        return None

    pool = ThreadPoolExecutor(max_workers=maximum_threads)
    with open(all_stock_file_path, 'r') as all_stocks:
        for stock_line in all_stocks:
            try:
                stock_symbol_and_name = stock_line.split()
                if len(stock_symbol_and_name) == 2:
                    stock_symbol = stock_symbol_and_name[0]
                    stock_name = stock_symbol_and_name[1]
                    if stock_name[-1] in stock_name_invalid_suffix:
                        stock_name = stock_name[:-1]
                    print(stock_symbol)
                    pool.submit(run_stock_scrapper, f'{stock_symbol} {stock_name}')
                    time.sleep(timeout_between_threads_creation)
            except:
                pass

    pool.shutdown(wait=True)
    end = time.time()
    print('Running all threads took {} seconds'.format(end - start))


def marketwatch_scrapper_main():
    iterate_over_all_stock()
    write_stocks_to_db()


if __name__ == "__main__":
    marketwatch_scrapper_main()
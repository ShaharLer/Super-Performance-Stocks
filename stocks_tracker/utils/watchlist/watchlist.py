from django.db.models import Q
from stocks_tracker.models import Stock
import json
from stocks_tracker.utils.breakout.breakout import *
import concurrent.futures
import getpass
import threading
import time as timer
import time
from yahoofinancials import YahooFinancials

lock = threading.Lock()
temp = 1
stocks_dict = {}
daily_avg_change = 0

def compare_stock_relative_volume_to_avg(stock):


    stock_current_volume = stock.get_current_volume()


    if (get_relative_market_time_today() == 0):
        return str(round((stock.get_current_volume() / stock.get_three_month_avg_daily_volume())*100,2))+'%'

    stock_3m_avg_relative_volume = stock.get_three_month_avg_daily_volume() * get_relative_market_time_today()
    return str(round((stock_current_volume / stock_3m_avg_relative_volume)*100,2)) + '%'

def update_volume_watchlist_stock_dict(stock):
    global stocks_dict
    #global temp
    global daily_avg_change

    stock_yahoo_obj = YahooFinancials(stock.symbol)
    stock_volume_increase_ratio = compare_stock_relative_volume_to_avg(stock_yahoo_obj)
    stock_price_change = stock_yahoo_obj.get_current_percent_change()
    stock_price_change = str(round((stock_price_change * 100 ),2))+'%'
    current_stock_price = round(stock_yahoo_obj.get_current_price(),2)
    stocks_dict[stock.symbol] = [stock.eps_growth,stock.net_income_growth,stock.sales_growth,stock_volume_increase_ratio,stock_price_change,current_stock_price]


def get_specific_stock(stock_symbol):
    stock = Stock.objects.get(symbol=stock_symbol)
    if (stock != None):
        lock.acquire()
        stock.is_stock_in_watchlist = True
        stock.save()
        lock.release()
    update_volume_watchlist_stock_dict(stock)
    print(stocks_dict)
    return json.loads(json.dumps(stocks_dict))

def watchlist_of_valid_stock():
    global stocks_dict
    stocks_dict = {}
    candidate_stocks = Stock.objects.filter(Q(is_stock_in_watchlist=True))
    start = time.time()
    if (len(candidate_stocks)!=0):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidate_stocks)) as executor:
            executor.map(update_volume_watchlist_stock_dict, candidate_stocks)

    end = time.time()
    print(f'Running all threads took {round(end - start, 2)} seconds')
    print(stocks_dict)
    return json.loads(json.dumps(stocks_dict))

def remove_stock_from_db(stock_symbol):
    stock = Stock.objects.get(symbol=stock_symbol)
    if (stock != None):
        lock.acquire()
        stock.is_stock_in_watchlist = False
        print(stock.is_stock_in_watchlist)
        stock.save()
        lock.release()

def watchlist_of_valid_stock_main():
   return watchlist_of_valid_stock()

if __name__ == "__main__":
    watchlist_of_valid_stock_main()

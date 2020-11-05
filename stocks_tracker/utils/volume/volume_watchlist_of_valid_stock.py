from django.db.models import Q
from stocks_tracker.models import Stock
from stocks_tracker.utils.technical.technical_analsys_of_stock import *
import json
from stocks_tracker.utils.breakout.breakout_stocks import *
import concurrent.futures
import getpass
import threading
import time as timer
import time
from yahoofinancials import YahooFinancials

temp = 1
stocks_dict = {}
daily_avg_change = 0

def compare_stock_relative_volume_to_avg(stock):
  #  global temp
   # temp = temp + 1
    #return temp
    stock_current_volume = stock.get_current_volume()
    stock_3m_avg_relative_volume = stock.get_three_month_avg_daily_volume() * get_relative_market_time_today()
    return stock_current_volume / stock_3m_avg_relative_volume

def update_volume_watchlist_stock_dict(stock):
    global stocks_dict
    #global temp
    global daily_avg_change

    stock_yahoo_obj = YahooFinancials(stock.symbol)
    stock_volume_increase_ratio = compare_stock_relative_volume_to_avg(stock_yahoo_obj)
    stock_price_change = stock_yahoo_obj.get_current_percent_change()
    #stock_price_change = temp
    daily_avg_change = daily_avg_change + stock_price_change
    stocks_dict[stock.symbol] = [stock.eps_growth,stock.net_income_growth,stock.sales_growth,stock_volume_increase_ratio,stock_price_change]


def volume_watchlist_of_valid_stock():
    global stocks_dict

    candidate_stocks = Stock.objects.filter(Q(is_technically_valid=True))
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidate_stocks)) as executor:
        executor.map(update_volume_watchlist_stock_dict, candidate_stocks)

    end = time.time()
    print(f'Running all threads took {round(end - start, 2)} seconds')
    print(daily_avg_change)
    stocks_dict['daily_avg_change'] = daily_avg_change
    return json.loads(json.dumps(stocks_dict))


def volume_watchlist_of_valid_stock_main():
   return volume_watchlist_of_valid_stock()

if __name__ == "__main__":
    volume_watchlist_of_valid_stock_main()
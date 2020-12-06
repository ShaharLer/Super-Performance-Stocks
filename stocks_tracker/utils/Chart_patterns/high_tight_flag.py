from yahoofinancials import YahooFinancials
import sys
import collections
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import os
import operator
from django.db.models import Q
import concurrent.futures
import datetime
from django.db.models import Q
from yahoofinancials import YahooFinancials
from stocks_tracker.models import Stock
import threading
from stocks_tracker.utils.technical.technical_analsys_of_stock import is_stock_technically_valid



###  Global Vars ###
lock = threading.Lock()
global_flag_dict = {}
###              ###

# Description -
#   return map of day number to list of date and price.
#   for example the first trading day will be 1 : [date, ma_value].
#   the indexing goal is to make it easier to iterate over the dates.
# [INT] ma_days - number of days for moving avg.
# [DICT] map_of_prices - keys are days number. values is list of [date,price]
def calculate_ma(ma_days, map_of_prices):
    map_of_ma = {}

    j = 0
    sum = 0

    for j in range(ma_days):
        sum = sum + map_of_prices[j][1]

    first_ma = sum / ma_days
    date_of_first_ma = map_of_prices[ma_days-1][0]
    map_of_ma[ma_days] = [date_of_first_ma,first_ma]

    for i in range(ma_days + 1,len(map_of_prices)):

        current_price = map_of_prices[i-1][1]
        price_to_ommit = map_of_prices[i-1-ma_days][1]
        value_to_add_to_ma = ( current_price - price_to_ommit ) / ma_days
        date = map_of_prices[i-1][0]
        new_ma = map_of_ma[i-1][1] + value_to_add_to_ma
        map_of_ma[i] = [date,new_ma]

    return map_of_ma


# Description -
#   return map of day number to list of date and price , or map of date to price, depends on the indexing flag
#   for example if indexing is true the first trading day will be 1 : [date, price_value]. otherwise, key is the date and price value is the value.
#   the indexing goal is to make it easier to iterate over the dates, as not every date is a trading day.
# [STR] symbol - stock symbol.
# [STR] start_date - date to start calculation for moving avg.
# [STR] end_date - date to end calculation for moving avg.
# [STR] period - time_interval can be either ‘daily’, ‘weekly’, or ‘monthly’. This variable determines the time period interval for your pull.
# [BOOL] indexing_flag - flag to determine the type of dict to return.
# return value - [DICT] map of day number to list of date and price , or map of date to price, depends on the indexing flag.
def get_map_of_date_to_price(symbol,start_date,end_date,period,indexing_flag):
    yahoo_stock = YahooFinancials(symbol)
    json = (yahoo_stock.get_historical_price_data(start_date, end_date, period))
    map_of_prices = {}

    x = 0
    for row in json[symbol]["prices"]:

        price_today = row['close']
        date = row['formatted_date']

        if indexing_flag == True:
            map_of_prices[x] = [date,price_today]

        else:
            map_of_prices[date] = price_today
        x = x+ 1
    return map_of_prices




# Description - stock surges 100% to 120% in four to eight weeks. The stock then corrects just 10% to 25% in price for only three to five weeks
# [OBJ] stock - stock object.
# return value - [STR] '' if stock is not high tight flag, details of the flag otherwise.
def is_high_tight_flag(stock):

    high_tight_flag_details = ''
    stock_symbol = stock.symbol

    stock_start_date = '2020-01-06'
    stock_end_date = str(datetime.date.today())
    index_after_surge  =  -1
    price_after_surge = -1
    index_before_surge = -1
    therteen_weeks_in_days = 65
    five_weeks_in_days = 25
    four_weeks_in_days = 20
    two_weeks_in_days = 10
    three_weeks_in_days = 15
    stock_surge_minimum = 2 # equals to 100 percent of stock surge
    stock_surge_maximum = 2.2 # equals increase of 120 percent in  stock price
    max_value_for_stock_allowed_to_drop_to = 0.75
    max_value_for_stock_allowed_to_go_high_to = 1.1

    map_with_index = get_map_of_date_to_price(stock_symbol,stock_start_date,stock_end_date,'daily',True)
    index_13_weeks_ago = list(map_with_index.keys())[-1] - therteen_weeks_in_days
    index_5_weeks_ago = list(map_with_index.keys())[-1] - five_weeks_in_days
    index_today = list(map_with_index.keys())[-1]

    # check that the stock surge between 100 to 120 percent in 4-8 weeks until the range of last 3 to 5 weeks
    for y in range (four_weeks_in_days,0,-1) :

        index_range_8_4_weeks = index_13_weeks_ago + y
        stock_surge = False
        # for every date between 13 weeks ago from today to 9 weeks ago from today, check if there was a date
        # between the last 2-5 weeks from today with a surge between 100 to 120 percent
        for x in range (three_weeks_in_days,0,-1):

            index_before_surge =  index_range_8_4_weeks + x
            price_before_surge = map_with_index[index_before_surge][1]
            index_after_surge  =  index_5_weeks_ago + x
            price_after_surge = map_with_index[index_after_surge][1]

            if price_after_surge >= stock_surge_minimum * price_before_surge and price_after_surge <= stock_surge_maximum * price_before_surge:
                stock_surge = True
                break
        else:
            continue
        break
    abort_stock = False

    if (stock_surge):

        # check that stock moving in the range of  +10% to -25% in price from the signal date to today
        for z in range(index_after_surge,index_today):
            index_between_surge_to_today =  z
            price_between_surge_to_today = map_with_index[index_between_surge_to_today][1]

            if (price_after_surge*max_value_for_stock_allowed_to_drop_to) >  price_between_surge_to_today or  (price_after_surge*max_value_for_stock_allowed_to_go_high_to) <  price_between_surge_to_today:
                abort_stock = True
                break

    if stock_surge and abort_stock == False  :

        high_tight_flag_details = ' start date is ' + str(map_with_index[index_before_surge][0]) +' with price of ' +  str(map_with_index[index_before_surge][1])+ '\n' \
                                  + ' changing date is ' + str(map_with_index[index_after_surge][0]) + ' with price of ' +  str(map_with_index[index_after_surge][1]) + '\n' \
                                  + ' from date '+  str(map_with_index[index_after_surge][0]) + ' consolidate  until today with upper range 10 percent to lower range 25'

        print(stock_symbol)
    return high_tight_flag_details


# Description - save stock stage number to database.
# [OBJ] stock - stock object.
# return value - None.
def update_global_dict(stock):
    is_flag = False
    high_tight_flag_data = is_high_tight_flag(stock)
    if high_tight_flag_data != '' and high_tight_flag_data != None :
        is_flag = True

    lock.acquire(2)
    try:
        global_flag_dict[stock]=[is_flag,high_tight_flag_data]
    except Exception as e: # work on python 3.x
        print(str(e))
        pass
    lock.release()


def high_tight_flag_main():


   candidate_stocks = Stock.objects.filter()
   with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidate_stocks)) as executor:
      executor.map(update_global_dict, candidate_stocks )

   for stock in global_flag_dict:
        stock.is_high_tight_flag_exists = global_flag_dict[stock][0]
        stock.high_tight_flag_data = global_flag_dict[stock][1]
        stock.save()


if __name__ == "__main__":
    high_tight_flag_main()

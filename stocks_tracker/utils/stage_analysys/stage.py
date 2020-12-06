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
#   return map of date as keys and ma_price as values
# [STR] symbol - stock symbol.
# [INT] ma_days - number of days for moving avg.
# [STR] start_date - date to start calculation for moving avg.
# [STR] end_date - date to end calculation for moving avg.
# [STR] period - time_interval can be either ‘daily’, ‘weekly’, or ‘monthly’. This variable determines the time period interval for your pull.
# return value - [DICT] map of date as keys and ma_price as values.
def get_ma_map(symbol,ma_days,start_date,end_date,period):

    map_of_prices_with_index = get_map_of_date_to_price(symbol,start_date,end_date,period,True)
    date_to_ma_with_index = calculate_ma(ma_days, map_of_prices_with_index)
    map_date_to_ma = dict()
    for x in date_to_ma_with_index :
        map_date_to_ma[date_to_ma_with_index[x][0]] = [date_to_ma_with_index[x][1]]


    return map_date_to_ma

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

#  Description - get list of all the list of stage 4 or 2, depend on stage_number var. stage 1,3 will be defined as the stages between them.
# [INT] stage_number - can ben 2 or 4.
# [DICT] date_to_ma_map - keys are dates, values are ma values.
# [DICT] date_to_price - keys are dates values are prices.
# [DICT] date_to_ma_map_helper - keys are dates, values are ma values.
#                                another ma map, greater the 30 weeks so temporary peeks during major up/down trends would not affect.
# [INT] stage_duration_days - minimum duration of every stage. the purpose  is to ignore not significant movements.
# Return value - [LIST] list of lists of the specific stage. every specific list will have a start and end date: [stage_start_date, stage_end_date].
def get_specific_stage_lst(stage_number,date_to_price,date_to_ma_map,date_to_ma_map_helper,stage_duration_days):

    if stage_number == 4 :
        op = operator.lt

    elif stage_number == 2:
        op = operator.gt

    index_keys_of_date_to_ma = list(date_to_ma_map.keys())
    index_values_of_date_to_ma = list(date_to_ma_map.values())

    index_keys_of_date_to_price = list(date_to_price.keys())

    #getting another ma map, greater the 30 weeks so temporary peeks during major up/down trends would not affect.
    index_keys_of_date_to_ma_helper = list(date_to_ma_map_helper.keys())
    index_values_of_date_to_ma_helper = list(date_to_ma_map_helper.values())

    start_date_stage = None
    stage_lst = []

    for date in date_to_price:

        if (date in date_to_ma_map ):

            date_index_price_map = index_keys_of_date_to_price.index(date)
            date_index_date_to_ma = index_keys_of_date_to_ma.index(date)
            ma_today = index_values_of_date_to_ma[date_index_date_to_ma][0]
            price_today = date_to_price[date]

            if date_index_date_to_ma+1 < len(index_values_of_date_to_ma):
                ma_tommorow = index_values_of_date_to_ma[date_index_date_to_ma+1][0]

            ma_differnce = (ma_tommorow - ma_today) / ma_today
            date_position = date_index_price_map


            # helper ma to prevent short temporary jump in a trend affect the stage result
            date_index_date_to_ma_helper = index_keys_of_date_to_ma_helper.index(date)
            ma_today_helper = index_values_of_date_to_ma_helper[date_index_date_to_ma_helper][0]

            if  op(ma_today,ma_today_helper):
                ma_to_use = ma_today_helper
            else:
                ma_to_use = ma_today

            if op(ma_differnce,0) and op(price_today,ma_to_use) :
                if start_date_stage == None :
                    start_date_index = date_index_price_map
                    start_date_stage = date

            elif start_date_stage != None:
                end_date_stage = index_keys_of_date_to_price[date_position]
                if (date_position - start_date_index > stage_duration_days ):
                    stage_lst.append([start_date_stage,end_date_stage])
                start_date_stage = None

    return stage_lst

# Description - fill the gaps between stage 2 and 4 , by adding lists of stage 1 and 3.
# [DICT] date_to_price - keys are dates , values their price.
# [LIST] sorted_list_of_stages - sorted list of stage lists. every stage list has two values : start_date_end_date.
#                                the list is sorted by dates.
# return value - [LIST] - sorted list of 1-4 lists stages.
def fill_stage1_and_stage3_lists(date_to_price,sorted_list_of_stages):

    new_list_with_1_and_3_stages = sorted_list_of_stages[:]
    index_keys_of_date_to_price = list(date_to_price.keys())
    for x in range(len(sorted_list_of_stages)-1):
        new_lst = [0,0]
        start_date_index_date_to_price = index_keys_of_date_to_price.index(sorted_list_of_stages[x][1])
        end_date_index_date_to_price = index_keys_of_date_to_price.index(sorted_list_of_stages[x+1][0])
        new_lst[0] = index_keys_of_date_to_price[start_date_index_date_to_price+1]
        new_lst[1] = index_keys_of_date_to_price[end_date_index_date_to_price-1]
        if new_lst[0] != new_lst[1] and  sorted_list_of_stages[x][1] != sorted_list_of_stages[x+1][0]  :
            new_list_with_1_and_3_stages.insert(x+1,new_lst)

    # fill the date between the last list to the last date
    if new_list_with_1_and_3_stages:
        last_date_index_date_to_price = index_keys_of_date_to_price.index(new_list_with_1_and_3_stages[len(new_list_with_1_and_3_stages)-1][1])
        new_lst = [0,0]
        new_lst[0] = index_keys_of_date_to_price[last_date_index_date_to_price+1]
        new_lst[1] = index_keys_of_date_to_price[-1]
        if new_lst[0] != new_lst[1]:
            new_list_with_1_and_3_stages.append(new_lst)

    new_list_with_1_and_3_stages = sorted(new_list_with_1_and_3_stages, key=lambda x: x[0])
    return new_list_with_1_and_3_stages

# Description - label every list to her stage.
# [LIST] list_of_stages - unlabelled list of stage lists.
# [LIST] stage_2_lst - list of stage 2 lists.
# [LIST] stage_4_lst - list of stage 4 lists.
# return value - [LIST] first param is stage number : 1-4 , second param is a lists of [stage_start_date,stage_end_date]
def label_list_to_stages(list_of_stages,stage_2_lst,stage_4_lst):

    labeled_list = []

    # label the lists by adding stage 4 and 2 first.
    for lst in list_of_stages:
        if lst in stage_4_lst:
            labeled_list.append([4,lst])
        elif lst in stage_2_lst:
            labeled_list.append([2,lst])
        else:
            labeled_list.append([0,lst])
    # adding stage 1 and 3
    for x in range (1,len(labeled_list)-1):
        if (labeled_list[x][0] == 0):

            if labeled_list[x-1][0] == 4 and labeled_list[x+1][0] == 2:
                labeled_list[x][0]= 1
            else:
                labeled_list[x][0]= 3

    if labeled_list:
        # label the last list:
        if labeled_list[-1][0] == 0:
            if labeled_list[-2][0] == 2:
                labeled_list[-1][0] = 3
            elif labeled_list[-2][0] == 4:
                labeled_list[-1][0] = 1
            else:
                #check_for_end_at_base_1_or_3(labeled_list[-1])
                labeled_list[-1][0] = 1
    labeled_list = sorted(labeled_list, key=lambda x: x[1][0])
    return labeled_list




# Description - main algoritmic function to calculate stages of a stock.
#               The algorithm works at this way:
#               1. calculate all the stage 2 and 4 dates.
#               2. fill the gaps between the stages. the gaps will be stage 1 or 3.
#               3. label every stage to his number. stage 3 will be between 2 and 4. stage 1 between 4 and 2.
# [DICT] date_to_ma_map - keys are dates, values are ma values.
# [DICT] date_to_price - keys are dates values are prices.
# [DICT] date_to_ma_map_helper - keys are dates, values are ma values.
#                                another ma map, greater the 30 weeks so temporary peeks during major up/down trends would not affect.
# return value - [LIST] first param is stage number : 1-4 , second param is a lists of [stage_start_date,stage_end_date]
def get_stage_of_stock(date_to_ma_map, date_to_price,date_to_ma_map_helper,stage_length):

    stage_2_lst = get_specific_stage_lst(2,date_to_price,date_to_ma_map,date_to_ma_map_helper,stage_length)
    stage_4_lst = get_specific_stage_lst(4,date_to_price,date_to_ma_map,date_to_ma_map_helper,stage_length)
    list_of_stages = stage_2_lst + stage_4_lst
    sorted_list_of_stages = sorted(list_of_stages, key=lambda x: x[0])
    list_of_stages = fill_stage1_and_stage3_lists(date_to_price,sorted_list_of_stages)
    labeled_list = label_list_to_stages(list_of_stages,stage_2_lst,stage_4_lst)
    return labeled_list

# Description - save stock stage number to database.
# [OBJ] stock - stock object.
# return value - None.
def update_db(stock):
    stock_symbol = stock.symbol
    ma_start_date = '2017-12-30' # should be at least 30 weeks lower start date from the stock start date.
    ma_helper_start_data = '2016-12-30' #  # should be at enough weeks lower start date from the stock start date.
    stock_start_date = '2018-07-06'
    stock_end_date = str(datetime.date.today())
    list_off_all_stages = get_stage_of_stock(get_ma_map(stock_symbol,150,ma_start_date,stock_end_date,'daily'),get_map_of_date_to_price(stock_symbol,stock_start_date,stock_end_date,'daily',False),get_ma_map(stock_symbol,190,ma_helper_start_data,stock_end_date,'daily'),150)
    if (len(list_off_all_stages)>0):
        lock.acquire(2)
        try:
            print(stock_symbol)
            if (isinstance(return_list[-1][0],int)):
                stock.current_stage_number =  list_off_all_stages[-1][0]
                stock.save()
        except:
            pass
        lock.release()

# Description - stock surges 100% to 120% in four to eight weeks. The stock then corrects just 10% to 25% in price for only three to five weeks
def is_high_tight_flag(stock):

    stock_symbol = stock.symbol

    stock_start_date = '2020-01-06'
    stock_end_date = str(datetime.date.today())
    index_after_surge  =  -1
    price_after_surge = -1
    index_before_surge = -1
    is_technically_valid = False
    therteen_weeks_in_days = 65
    five_weeks_in_days = 25
    four_weeks_in_days = 20
    two_weeks_in_days = 10
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
        # between the last 3-5 weeks from today with a surge between 100 to 120 percent
        for x in range (two_weeks_in_days,0,-1):

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
        yahoo_stock = YahooFinancials(stock.symbol)
        is_technically_valid = is_stock_technically_valid(yahoo_stock)
        if is_technically_valid:
            print(stock_symbol)
            print(' start date is ' + str(map_with_index[index_before_surge][0]) +' with price of ' +  str(map_with_index[index_before_surge][1]))
            print(' changing date is ' + str(map_with_index[index_after_surge][0]) + ' with price of ' +  str(map_with_index[index_after_surge][1]))
            print(' from date '+  str(map_with_index[index_after_surge][0]) + ' consalidate  until today with upper range 10 percent to lower range 25')


def stage_main():


    candidate_stocks = Stock.objects.filter()
    print(candidate_stocks)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidate_stocks)) as executor:
        executor.map(is_high_tight_flag, candidate_stocks)




if __name__ == "__main__":
    stage_main()

from yahoofinancials import YahooFinancials
import sys
import collections
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import os
import datetime
import trendln
# this will serve as an example for security or index closing prices, or low and high prices
import yfinance as yf # requires yfinance - pip install yfinance
import matplotlib
import findiff
import  numdifftools


nyse_composite_index_symbol = '^NYA'
dow_index_symbol = '^DJI'
sp500_index_symbol = '^GSPC'
nasdaq_composite_symbol = '^IXIC'
start_date = '2019-01-01'
end_date = '2020-11-11'
number_of_distribution_dates_to_look_for = 4
number_of_days_of_of_total_distribution = 25
number_of_days_to_check_for_down = 20
precent_down = 0.05
top_width = 20
precent_down_for_index_dips = 0.05

class index_set():

    def __init__(self):
        self.major_index_set = set()
        self.major_index_set.add(nyse_composite_index_symbol)
        self.major_index_set.add(dow_index_symbol)
        self.major_index_set.add(sp500_index_symbol)
        self.major_index_set.add(nasdaq_composite_symbol)


def is_disturbtion_day(volume_yesterday, volume_today, price_today, price_yesterday):

    is_disturbtion_day = False

    if ( volume_today > volume_yesterday ) and (price_today <= 0.998 * price_yesterday) :
        is_disturbtion_day = True

    return is_disturbtion_day


def get_distribution_dict(index_symbol,start_date,end_date):
    yahoo_stock = YahooFinancials(index_symbol)
    json = (yahoo_stock.get_historical_price_data(start_date,end_date, 'daily'))
    price_yesterday = sys.maxsize
    volume_yesterday = sys.maxsize
    days_counter = 1
    days_counter_of_25_days = 0

    disturbtion_dict = {}
    disturbtion_dict_set = set()

    for row in json[index_symbol]["prices"]:
        volume_today = row['volume']
        price_today = row['close']
        date = row['formatted_date']

        is_disturbtion = is_disturbtion_day(volume_yesterday, volume_today, price_today, price_yesterday)
        if (is_disturbtion ):
            disturbtion_dict[days_counter] = [date,price_today]
            days_counter_of_25_days = 0
            disturbtion_dict_set.add(date)


        volume_yesterday = volume_today
        price_yesterday = price_today
        days_counter = days_counter + 1
        days_counter_of_25_days = days_counter_of_25_days + 1


    return  disturbtion_dict


def clean_distribution_list(distribution_dict,map_of_index,index_symbol):

    distribution_set = set()

    more_than_5_precent_set = set()
    keys = list(map_of_index.keys())
    values = list(map_of_index.values())

    for date_num in distribution_dict:
        if distribution_dict[date_num][0] in keys:
            date_index = keys.index(distribution_dict[date_num][0])

            for x in range (25) :

                if (x+date_index >= len(keys) ):
                    break

                if values[x+date_index] >= values[date_index] * 1.05 :
                    more_than_5_precent_set.add(date_num)
                    break

    for day_key in more_than_5_precent_set:
        del distribution_dict[day_key]

    for index in distribution_dict:
        distribution_set.add(distribution_dict[index][0])

    return distribution_set

def get_index_data_map(yahoo_stock,index_symbol,distribution_dict_set):

    array_of_index_details= []
    json = (yahoo_stock.get_historical_price_data(start_date, end_date, 'daily'))

    for row in json[index_symbol]["prices"]:
        map_today = {}
        map_today['close'] = row['close']
        map_today['open'] = row['open']
        map_today['high'] = row['high']
        map_today['low'] = row['low']
        map_today['volume'] = row['volume']
        map_today['date'] = row['formatted_date']
        if map_today['date'] in distribution_dict_set :
            map_today['is_distribution'] = 1
        else:
            map_today['is_distribution'] = 0
        array_of_index_details.append(map_today)

    return array_of_index_details


def get_map_of_date_to_price(yahoo_stock,index_symbol):

    map_date_to_price = {}
    json = (yahoo_stock.get_historical_price_data(start_date, end_date, 'daily'))

    for row in json[index_symbol]["prices"]:

        price_today = row['close']
        date_today = row['formatted_date']
        map_date_to_price[date_today] = price_today

    return map_date_to_price


def get_yahoo_finance_historical_price_data():

    map_of_all_index_date_to_price = {}

    nyse_map = get_map_of_date_to_price( YahooFinancials(nyse_composite_index_symbol), nyse_composite_index_symbol )
    dow_map = get_map_of_date_to_price( YahooFinancials(dow_index_symbol), dow_index_symbol )
    nasdaq_map = get_map_of_date_to_price( YahooFinancials(nasdaq_composite_symbol), nasdaq_composite_symbol )
    sp500_map = get_map_of_date_to_price( YahooFinancials(sp500_index_symbol), sp500_index_symbol )

    map_of_all_index_date_to_price[nyse_composite_index_symbol] = nyse_map
    map_of_all_index_date_to_price[dow_index_symbol] = dow_map
    map_of_all_index_date_to_price[nasdaq_composite_symbol] = nasdaq_map
    map_of_all_index_date_to_price[sp500_index_symbol] = sp500_map

    return map_of_all_index_date_to_price


def get_distribution_days(start_date,end_date,major_index_set):

    map_of_all_index_date_to_price = get_yahoo_finance_historical_price_data ()
    print(map_of_all_index_date_to_price)
    for index_symbol in major_index_set:
        distribution_dict = get_distribution_dict(index_symbol, start_date,end_date)
        distribution_dict = clean_distribution_list(distribution_dict,map_of_all_index_date_to_price, index_symbol)


def get_index_ready_to_send():

    distribution_set = clean_distribution_list(get_distribution_dict(nasdaq_composite_symbol, start_date,end_date),get_map_of_date_to_price(YahooFinancials(nasdaq_composite_symbol),nasdaq_composite_symbol), nasdaq_composite_symbol)
    dow_map = get_index_data_map( YahooFinancials(nasdaq_composite_symbol), nasdaq_composite_symbol,distribution_set )
  #  print(dow_map)
    return dow_map


def market_top_main():



    index_object = index_set()

    # return and print an ordered list with the best params. look inside the function for the starting value to configure.
    start_date = '2020-01-06'
    end_date = str(datetime.date.today())
   # return get_distribution_days(start_date,end_date,index_object.major_index_set)




    return get_index_ready_to_send()



if __name__ == "__main__":
    market_top_main()

import concurrent.futures
from datetime import datetime, timedelta, date, time
from heapq import heappush, heappop

import pandas_market_calendars
import pytz
from pandas.tseries.offsets import BDay
from yahoofinancials import YahooFinancials

from .nasdaq_composite import *

NASDAQ_COMPOSITE_SYMBOL = '^IXIC'
NYSE_CALENDAR = pandas_market_calendars.get_calendar('NYSE')
US_EASTERN = 'US/Eastern'
START_OF_TODAY = datetime.combine(date.today(), time())
MARKET_START_TIME = START_OF_TODAY.replace(hour=8, minute=30, second=0)  # change according to winter clock

nasdaq_stock = YahooFinancials(NASDAQ_COMPOSITE_SYMBOL)
nasdaq_heap = []


def update_nasdaq_stock(stock, ma_3_change, ma_7_change, buy_market):
    stock.set_ma_3_change(ma_3_change)
    stock.set_ma_7_change(ma_7_change)
    stock.set_is_a_buy_market(buy_market)


def is_a_buy_market(current_ma_3, current_ma_7, current_ma_3_change, current_ma_7_change):
    return current_ma_3 > current_ma_7 and current_ma_3_change > current_ma_7_change > 0


def get_moving_avg_change(current_moving_avg, prev_moving_avg):
    return round((current_moving_avg - prev_moving_avg) / prev_moving_avg * 100, 2)


def calc_and_update_nasdaq_stock(current_day_nasdaq_stock, prev_day_nasdaq_stock):
    current_ma_3 = current_day_nasdaq_stock.get_ma_3()
    current_ma_7 = current_day_nasdaq_stock.get_ma_7()
    ma_3_change = get_moving_avg_change(current_ma_3, prev_day_nasdaq_stock.get_ma_3())
    ma_7_change = get_moving_avg_change(current_ma_7, prev_day_nasdaq_stock.get_ma_7())
    buy_market = is_a_buy_market(current_ma_3, current_ma_7, ma_3_change, ma_7_change)
    update_nasdaq_stock(current_day_nasdaq_stock, ma_3_change, ma_7_change, buy_market)


def calculate_nasdaq_objects_list():
    # we need at least 2 objects in order to get changes in the moving avg
    if len(nasdaq_heap) < 2:
        return None

    nasdaq_objects_list = []
    prev_day_nasdaq_stock = None

    while nasdaq_heap:
        current_day_nasdaq_stock = prev_day_nasdaq_stock if nasdaq_objects_list else heappop(nasdaq_heap)
        prev_day_nasdaq_stock = heappop(nasdaq_heap)
        calc_and_update_nasdaq_stock(current_day_nasdaq_stock, prev_day_nasdaq_stock)
        nasdaq_objects_list.append(current_day_nasdaq_stock)
    return nasdaq_objects_list


def calc_moving_avg_by_parameter(historical_prices, ma_parameter):
    sum_of_prices = 0
    for i in range(ma_parameter):
        price = historical_prices[i]['close']
        sum_of_prices += price
    return sum_of_prices / ma_parameter


def calc_historical_prices(stock, ma_calc_end_range, trading_days_to_reach):
    business_days_to_go_back = trading_days_to_reach
    while True:
        ma_calc_start_range = ma_calc_end_range - BDay(business_days_to_go_back)
        historical_prices = stock.get_historical_price_data(start_date=ma_calc_start_range.strftime('%Y-%m-%d'),
                                                            end_date=ma_calc_end_range.strftime('%Y-%m-%d'),
                                                            time_interval='daily')[NASDAQ_COMPOSITE_SYMBOL]['prices']
        if len(historical_prices) < trading_days_to_reach:
            business_days_to_go_back += 1
        else:
            return historical_prices


def get_moving_avg_by_parameter(trading_day, moving_avg_duration):
    historical_prices = calc_historical_prices(nasdaq_stock, trading_day + timedelta(days=1), moving_avg_duration)
    ma_by_parameter = calc_moving_avg_by_parameter(historical_prices, moving_avg_duration)
    return round(ma_by_parameter, 2)


def calculate_nasdaq_composite_info(trading_day):
    global nasdaq_heap
    ma_3 = get_moving_avg_by_parameter(trading_day, 3)
    ma_7 = get_moving_avg_by_parameter(trading_day, 7)
    if ma_3 and ma_7:
        heappush(nasdaq_heap, NasdaqComposite(date=trading_day, ma_3=ma_3, ma_7=ma_7))


def get_nasdaq_composite_info(business_days_list):
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(business_days_list)) as executor:
            executor.map(calculate_nasdaq_composite_info, business_days_list)
    except Exception as e:
        print(str(e))
        return None

    if len(nasdaq_heap) < len(business_days_list):
        return None

    nasdaq_composite_list = calculate_nasdaq_objects_list()
    return nasdaq_composite_list


def is_before_market_open_time():
    wall_street_timezone = pytz.timezone(US_EASTERN)
    wallstreet_local_time_now = datetime.now(wall_street_timezone).replace(tzinfo=None)
    return wallstreet_local_time_now < MARKET_START_TIME


def is_trading_day(date_to_check):
    formatted_date = date_to_check.strftime('%Y-%m-%d')
    return not NYSE_CALENDAR.schedule(start_date=formatted_date, end_date=formatted_date).empty


def calc_closest_trading_date_going_back(day):
    today = datetime.today().date()
    day = today if day > today else day

    while not is_trading_day(day) or (day == today and is_before_market_open_time()):
        day = (day - BDay(1)).date()
        while not is_trading_day(day):
            day = (day - BDay(1)).date()
    return day


def get_business_days_list(from_date, to_date):
    business_days_list = []
    closest_trading_day = calc_closest_trading_date_going_back(to_date)

    # we need at least 2 days in order to calculate later moving avg changes
    while len(business_days_list) < 2 or business_days_list[-1] >= from_date:
        business_days_list.append(closest_trading_day)
        closest_trading_day = calc_closest_trading_date_going_back((closest_trading_day - BDay(1)).date())

    return business_days_list


def nasdaq_composite_info_main(from_date, to_date):
    business_days_list = get_business_days_list(from_date, to_date)
    nasdaq_composite_list = get_nasdaq_composite_info(business_days_list)
    return nasdaq_composite_list


if __name__ == "__main__":
    nasdaq_composite_info_main(datetime.today().date(), datetime.today().date())

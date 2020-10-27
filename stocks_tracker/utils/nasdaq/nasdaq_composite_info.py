from datetime import datetime, timedelta, date, time
from enum import Enum
from collections import OrderedDict

import pandas_market_calendars
import pytz
from pandas.tseries.offsets import BDay
from yahoofinancials import YahooFinancials

from .nasdaq_composite import *

NASDAQ_COMPOSITE_SYMBOL = '^IXIC'
US_EASTERN = 'US/Eastern'
START_OF_TODAY = datetime.combine(date.today(), time())
MARKET_START_TIME = START_OF_TODAY.replace(hour=9, minute=30, second=0)
MARKET_END_TIME = START_OF_TODAY.replace(hour=16, minute=0, second=0)
NYSE_CALENDAR = pandas_market_calendars.get_calendar('NYSE')


class MarketStatus(Enum):
    BEFORE_MARKET_OPEN = 'before market open'
    TRADING_TIME = 'trading time'
    AFTER_MARKET_CLOSED = 'after market closed'
    MARKET_CLOSED_TODAY = 'market closed today'


def update_nasdaq_composite_object(nasdaq_composite_object, ma_3_change, ma_7_change, buy_market):
    nasdaq_composite_object.set_ma_3_change(ma_3_change)
    nasdaq_composite_object.set_ma_7_change(ma_7_change)
    nasdaq_composite_object.set_is_a_buy_market(buy_market)


def handle_nasdaq_composite_previous_day(trading_day, ma_3, ma_7, nasdaq_dict):
    nasdaq_composite_object = NasdaqComposite(date=trading_day, ma_3=ma_3, ma_7=ma_7)
    nasdaq_dict[trading_day] = nasdaq_composite_object


def handle_nasdaq_composite_current_day(day, ma_3, ma_7, ma_3_change, ma_7_change, buy_market, nasdaq_dict):
    if day in nasdaq_dict:
        update_nasdaq_composite_object(nasdaq_dict[day], ma_3_change, ma_7_change, buy_market)
    else:
        nasdaq_composite_object = NasdaqComposite(day, ma_3, ma_7, ma_3_change, ma_7_change, buy_market)
        nasdaq_dict[day] = nasdaq_composite_object


def is_a_buy_market(current_ma_3, current_ma_7, current_ma_3_change, current_ma_7_change):
    return current_ma_3 > current_ma_7 and current_ma_3_change > current_ma_7_change > 0


def get_last_ma_change(first_ma, second_ma):
    return round((second_ma - first_ma) / first_ma * 100, 2)


def calc_ma_by_parameter(historical_prices, ma_parameter):
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


def get_moving_avg_by_parameter_and_last_trading_day(stock, ma_parameter, day_to_calc_ma_for):
    try:
        historical_prices = calc_historical_prices(stock, day_to_calc_ma_for + timedelta(days=1), ma_parameter)
        ma_by_parameter = calc_ma_by_parameter(historical_prices, ma_parameter)
        return round(ma_by_parameter, 2)
    except Exception as e:
        print(str(e))


def get_3day_moving_avg(stock, day, nasdaq_dict):
    if day in nasdaq_dict:
        return nasdaq_dict[day].get_ma_3()
    return get_moving_avg_by_parameter_and_last_trading_day(stock, 3, day)


def get_7day_moving_avg(stock, day, nasdaq_dict):
    if day in nasdaq_dict:
        return nasdaq_dict[day].get_ma_7()
    return get_moving_avg_by_parameter_and_last_trading_day(stock, 7, day)


def is_trading_day(date_to_check):
    formatted_date = date_to_check.strftime('%Y-%m-%d')
    return not NYSE_CALENDAR.schedule(start_date=formatted_date, end_date=formatted_date).empty


def is_before_market_open_time():
    wall_street_timezone = pytz.timezone(US_EASTERN)
    wallstreet_local_time_now = datetime.now(wall_street_timezone).replace(tzinfo=None)
    return wallstreet_local_time_now < MARKET_START_TIME


def calculate_nasdaq_composite_info_for_date(stock, trading_day, nasdaq_dict):
    ma_3 = get_3day_moving_avg(stock, trading_day, nasdaq_dict)
    ma_7 = get_7day_moving_avg(stock, trading_day, nasdaq_dict)

    previous_business_date = (trading_day - BDay(1)).date()
    previous_trading_day = calc_closest_trading_date_going_back(previous_business_date)
    previous_ma_3 = get_3day_moving_avg(stock, previous_trading_day, nasdaq_dict)
    previous_ma_7 = get_7day_moving_avg(stock, previous_trading_day, nasdaq_dict)

    if ma_3 is None or ma_7 is None or previous_ma_3 is None or previous_ma_7 is None:
        return None

    ma_3_change = get_last_ma_change(previous_ma_3, ma_3)
    ma_7_change = get_last_ma_change(previous_ma_7, ma_7)
    buy_market = is_a_buy_market(ma_3, ma_7, ma_3_change, ma_7_change)

    handle_nasdaq_composite_current_day(trading_day, ma_3, ma_7, ma_3_change, ma_7_change, buy_market, nasdaq_dict)
    handle_nasdaq_composite_previous_day(previous_trading_day, previous_ma_3, previous_ma_7, nasdaq_dict)
    return True


def calc_closest_trading_date_going_back(day):
    today = datetime.today().date()
    day = today if day > today else day

    while not is_trading_day(day) or (day == today and is_before_market_open_time()):
        day = (day - BDay(1)).date()
        while not is_trading_day(day):
            day = (day - BDay(1)).date()
    return day


def calculate_nasdaq_composite_info_dates_range(stock, start_date, end_date):
    nasdaq_component_dict = OrderedDict()
    closest_trading_day = calc_closest_trading_date_going_back(end_date)
    while closest_trading_day >= start_date or len(nasdaq_component_dict) == 0:
        if not calculate_nasdaq_composite_info_for_date(stock, closest_trading_day, nasdaq_component_dict):
            return None
        previous_business_day = (closest_trading_day - BDay(1)).date()
        closest_trading_day = calc_closest_trading_date_going_back(previous_business_day)

    nasdaq_composite_list = list(nasdaq_component_dict.values())[:-1]
    return nasdaq_composite_list


def nasdaq_composite_info_main(start_date=datetime.today().date(), end_date=datetime.today().date()):
    yahoo_stock = YahooFinancials(NASDAQ_COMPOSITE_SYMBOL)
    nasdaq_composite_list = calculate_nasdaq_composite_info_dates_range(yahoo_stock, start_date, end_date)
    return nasdaq_composite_list


if __name__ == "__main__":
    nasdaq_composite_info_main()

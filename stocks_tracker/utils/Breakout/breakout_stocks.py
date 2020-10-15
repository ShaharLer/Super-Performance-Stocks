from stocks_tracker.models import Stock
from yahoofinancials import YahooFinancials
from datetime import datetime, date, time
import concurrent.futures
import pytz

US_EASTERN = 'US/Eastern'
MARKET_START_HOURS = 9
MARKET_START_MINUTES = 30
MARKET_END_HOURS = 16
MARKET_END_MINUTES = 0
START_OF_TODAY = datetime.combine(date.today(), time())
MARKET_START_TIME = START_OF_TODAY.replace(hour=MARKET_START_HOURS, minute=MARKET_START_MINUTES)
MARKET_END_TIME = START_OF_TODAY.replace(hour=MARKET_END_HOURS, minute=MARKET_END_MINUTES)
TOTAL_DAILY_MARKET_TIME_IN_MINUTES = int((MARKET_END_TIME - MARKET_START_TIME).total_seconds() / 60)
VOLUME_THRESHOLD = 1.2
STOCK_PERCENT_CHANGE_THRESHOLD = 0.02


def get_relative_market_time_today():
    wallstreet_local_time_now = datetime.now(pytz.timezone(US_EASTERN)).replace(tzinfo=None)
    if wallstreet_local_time_now < MARKET_START_TIME:
        return 0
    elif wallstreet_local_time_now > MARKET_END_TIME:
        return 1
    else:
        market_time_in_minutes_today = int((wallstreet_local_time_now - MARKET_START_TIME).total_seconds() / 60)
        return market_time_in_minutes_today / TOTAL_DAILY_MARKET_TIME_IN_MINUTES


def is_stock_in_breakout(stock):
    stock_current_volume = stock.get_current_volume()
    stock_3m_avg_relative_volume = stock.get_three_month_avg_daily_volume() * get_relative_market_time_today()
    stock_current_percent_change = stock.get_current_percent_change()

    return (stock_current_volume >= stock_3m_avg_relative_volume * VOLUME_THRESHOLD) \
           and stock_current_percent_change >= STOCK_PERCENT_CHANGE_THRESHOLD


def calc_stock_breakout(stock):
    yahoo_stock = YahooFinancials(stock.symbol)
    stock.is_in_breakout = is_stock_in_breakout(yahoo_stock)
    stock.save()


def is_market_open():
    wallstreet_local_time_now = datetime.now(pytz.timezone(US_EASTERN)).replace(tzinfo=None)
    return MARKET_START_TIME <= wallstreet_local_time_now <= MARKET_END_TIME


def breakout_stocks_main():
    if not is_market_open():
        return False

    candidate_stocks = Stock.objects.filter(is_technically_valid=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidate_stocks)) as executor:
        executor.map(calc_stock_breakout, candidate_stocks)


if __name__ == "__main__":
    breakout_stocks_main()

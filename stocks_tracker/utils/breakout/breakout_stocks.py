import concurrent.futures
import getpass
import threading
import time as timer
from datetime import datetime, date, time
import yfinance as yf # requires yfinance - pip install yfinance
import pytz
from yahoofinancials import YahooFinancials

from stocks_tracker.models import Stock
from .social_media import SocialMedia

US_EASTERN = 'US/Eastern'
START_OF_TODAY = datetime.combine(date.today(), time())
MARKET_START_TIME = START_OF_TODAY.replace(hour=9, minute=30)
MARKET_END_TIME = START_OF_TODAY.replace(hour=16, minute=0)
TOTAL_DAILY_MARKET_TIME_IN_MINUTES = int((MARKET_END_TIME - MARKET_START_TIME).total_seconds() / 60)
NON_MARKET_DAYS = [5, 6]
TIMEOUT_BETWEEN_BREAKOUT_RUNS_MINUTES = 10
VOLUME_THRESHOLD = 1.4
STOCK_PERCENT_CHANGE_THRESHOLD = 0.023
BREAKOUT_EMAIL_RECIPIENTS = ['aradinbar91@gmail.com', 'shaharman5@gmail.com']
lock = threading.Lock()
social_media = SocialMedia()


def send_alerts(stock_symbol, stock_volume_increase_ratio,stock_sector,stock_industry):
    message_to_send = f'Breakout!!! Buy alert for {stock_symbol}, as volume is bigger than the average by ' \
                      f'{stock_volume_increase_ratio}' + ' sector is ' + stock_sector + ' industry is ' + stock_industry
    print(message_to_send)
    lock.acquire()
    try:
        # social_media.send_whatsapp_message('"Stocks alerts"', message_to_send) TODO decide if should stay
        social_media.send_gmail_message(BREAKOUT_EMAIL_RECIPIENTS, message_to_send)
    except KeyboardInterrupt:
        print('Sending alerts thread was closed by user')
    finally:
        lock.release()


def get_relative_market_time_today():
    wallstreet_local_time_now = datetime.now(pytz.timezone(US_EASTERN)).replace(tzinfo=None)
    if wallstreet_local_time_now < MARKET_START_TIME:
        return 0
    elif wallstreet_local_time_now > MARKET_END_TIME:
        return 1
    else:
        market_time_in_minutes_today = int((wallstreet_local_time_now - MARKET_START_TIME).total_seconds() / 60)
        return market_time_in_minutes_today / TOTAL_DAILY_MARKET_TIME_IN_MINUTES


def get_stock_volume_increase_ratio(stock, pivot_point):
    stock_current_volume = stock.get_current_volume()
    stock_3m_avg_relative_volume = stock.get_three_month_avg_daily_volume() * get_relative_market_time_today()
    stock_current_percent_change = stock.get_current_percent_change()
    stock_current_price = stock.get_current_price()
    is_in_breakout = (stock_current_volume >= stock_3m_avg_relative_volume * VOLUME_THRESHOLD) \
                        and stock_current_percent_change >= STOCK_PERCENT_CHANGE_THRESHOLD \
                        and stock_current_price >= pivot_point

    return (stock_current_volume / stock_3m_avg_relative_volume * VOLUME_THRESHOLD) if is_in_breakout else None


def calc_stock_breakout(stock):
    stock_volume_increase_ratio = get_stock_volume_increase_ratio(YahooFinancials(stock.symbol), stock.pivot)
    if stock_volume_increase_ratio:  # detected breakout
        stock.last_breakout = date.today()
        stock.save()
        object_for_more_data = yf.Ticker(stock.symbol)
        send_alerts(stock.symbol, stock_volume_increase_ratio,object_for_more_data.info['sector'],object_for_more_data.info['industry'])
    else:
        print(f'No breakout so far for: {stock.symbol}')


def is_market_open():
    wallstreet_local_time_now = datetime.now(pytz.timezone(US_EASTERN)).replace(tzinfo=None)
    week_day = wallstreet_local_time_now.weekday()
    return (week_day not in NON_MARKET_DAYS) and (MARKET_START_TIME <= wallstreet_local_time_now <= MARKET_END_TIME)


def detect_breakouts():
    candidate_stocks = Stock.objects.filter(is_accelerated=True).exclude(pivot=None)
    if candidate_stocks:
        while is_market_open():
            print('\nRunning again!')
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidate_stocks)) as executor:
                executor.map(calc_stock_breakout, candidate_stocks)
            print(f'Waiting {TIMEOUT_BETWEEN_BREAKOUT_RUNS_MINUTES} minutes before next run...')
            timer.sleep(TIMEOUT_BETWEEN_BREAKOUT_RUNS_MINUTES * 60)
        print('Market is closed!')
    else:
        print('There are no stocks with pivot set')


def run_breakout_threads():
    try:
        thread = threading.Thread(target=detect_breakouts)
        thread.daemon = True
        thread.start()
        while thread.is_alive():
            thread.join(1)
    except (KeyboardInterrupt, SystemExit):
        print('Program was closed by user')


def breakout_stocks_main():
    global social_media
    password = getpass.getpass('Enter the email notifications password: ')
    social_media.set_password(password)
    run_breakout_threads()


if __name__ == "__main__":
    breakout_stocks_main()

import concurrent.futures
import threading
import time as timer
from datetime import datetime, date, time
import yfinance as yf
import pandas_market_calendars
import pytz
from background_task import background
from django.db.models import Q
from django.utils import timezone
from yahoofinancials import YahooFinancials
from stocks_tracker.utils.stock_stats.stock_stats import *
from stocks_tracker.models import *
from .social_media import SocialMedia

US_EASTERN = 'US/Eastern'
NYSE_CALENDAR = pandas_market_calendars.get_calendar('NYSE')
START_OF_TODAY = datetime.combine(date.today(), time())
MARKET_START_TIME = START_OF_TODAY.replace(hour=9, minute=30)
MARKET_END_TIME = START_OF_TODAY.replace(hour=16, minute=0)
TOTAL_DAILY_MARKET_TIME_IN_MINUTES = int((MARKET_END_TIME - MARKET_START_TIME).total_seconds() / 60)
NON_MARKET_DAYS = [5, 6]
TIMEOUT_BETWEEN_BREAKOUT_RUNS_MINUTES = 15
VOLUME_THRESHOLD = 1.4
STOCK_PERCENT_CHANGE_THRESHOLD = 0.023
BREAKOUT_EMAIL_RECIPIENTS = ['aradinbar91@gmail.com', 'shaharman5@gmail.com', 'tkhtur1@gmail.com']
lock = threading.Lock()
social_media = SocialMedia()
breakouts = set()


def update_stocks_breakout_in_db():
    for stock in breakouts:
        try:
            stock.save()
        except Exception as e:
            print(f'Failed to update breakout for stock {stock.symbol} in the DB: {str(e)}')


def send_alerts(stock_symbol, stock_volume_increase_ratio, stock_sector, stock_industry):
    message_to_send = f'Breakout!!! Buy alert for {stock_symbol}.' \
                      f'\nCurrent volume is {stock_volume_increase_ratio} times bigger than relational average volume.' \
                      f'\nSector: {stock_sector}' \
                      f'\nIndustry: {stock_industry}'
    lock.acquire()
    try:
        # social_media.send_whatsapp_message('"Stocks alerts"', message_to_send) TODO decide if should stay
        social_media.send_gmail_message(BREAKOUT_EMAIL_RECIPIENTS, message_to_send)
    except KeyboardInterrupt:
        print('Sending alerts thread was closed by user')
    except Exception as e:
        print(f'Failed to send email of breakout for the stock {stock_symbol}')
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
        stock.is_breakout = True
        stock.last_breakout = timezone.now()
        breakouts.add(stock)
        print(f'{stock.symbol}: BREAKOUT!!!')
        object_for_more_data = yf.Ticker(stock.symbol)  # TODO create DB fields and move to scrapper
        sector = object_for_more_data.info['sector']
        industry = object_for_more_data.info['industry']
        send_alerts(stock.symbol, round(stock_volume_increase_ratio, 2), sector, industry)
        create_new_stock_stat(stock.symbol, stock.pivot, str(datetime.date.today()))
    else:
        print(f'{stock.symbol}: No breakout')


def is_today_a_trading_day():
    try:
        formatted_date = datetime.today().strftime('%Y-%m-%d')
        return not NYSE_CALENDAR.schedule(start_date=formatted_date, end_date=formatted_date).empty
    except Exception as e:
        print(str(e))
        raise Exception


def is_market_open():
    wall_street_timezone = pytz.timezone(US_EASTERN)
    wallstreet_local_time_now = datetime.now(wall_street_timezone).replace(tzinfo=None)
    return MARKET_START_TIME < wallstreet_local_time_now < MARKET_END_TIME


def detect_breakouts():
    global breakouts
    while is_market_open():
        candidate_stocks = Stock.objects.filter(is_technically_valid=True).exclude(Q(pivot=None) | Q(is_breakout=True))
        if candidate_stocks:
            print(f'\nRunning breakout detection again!')
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidate_stocks)) as executor:
                executor.map(calc_stock_breakout, candidate_stocks)
            update_stocks_breakout_in_db()

            print(f'Waiting {TIMEOUT_BETWEEN_BREAKOUT_RUNS_MINUTES} minutes from before next run...')
            timer.sleep(TIMEOUT_BETWEEN_BREAKOUT_RUNS_MINUTES * 60)
        else:
            print('There are no more stocks with pivot set that do not have breakout\nExiting...')
            return
    print('Market is closed!\nExiting...')


def run_breakout_threads():
    try:
        thread = threading.Thread(target=detect_breakouts)
        thread.daemon = True
        thread.start()
        while thread.is_alive():
            thread.join(1)
    except (KeyboardInterrupt, SystemExit):
        print('Program was closed by user')


@background()
def breakout_main(password=''):
    print('Going to run breakout detection')
    if not is_today_a_trading_day():
        print('Today there is no trading in the NYSE')
        return

    global social_media
    social_media.set_password(password)
    run_breakout_threads()

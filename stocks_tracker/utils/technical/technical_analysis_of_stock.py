import concurrent.futures

from background_task import background
from django.db.models import Q
from django.utils import timezone
from yahoofinancials import YahooFinancials

from stocks_tracker.models import Stock

STOCK_YEARLY_HIGH_MULTIPLIER = 0.75
STOCK_YEARLY_LOW_MULTIPLIER = 1.3


def is_stock_technically_valid(stock):
    stock_50_ma = stock.get_50day_moving_avg()
    stock_200_ma = stock.get_200day_moving_avg()
    stock_yearly_high = stock.get_yearly_high()
    stock_yearly_low = stock.get_yearly_low()
    stock_current_price = stock.get_current_price()

    if not stock_50_ma or not stock_200_ma or not stock_yearly_high or not stock_yearly_low or not stock_current_price:
        return False

    return stock_current_price >= stock_50_ma > stock_200_ma \
           and stock_current_price >= (stock_yearly_high * STOCK_YEARLY_HIGH_MULTIPLIER) \
           and stock_current_price >= (stock_yearly_low * STOCK_YEARLY_LOW_MULTIPLIER)


def calc_stock_technical_validation(stock):
    try:
        yahoo_stock = YahooFinancials(stock.symbol)
        stock.is_technically_valid = is_stock_technically_valid(yahoo_stock)
        stock.last_technically_valid_update = timezone.now
        stock.save()
    except:
        print(f'Failed to save stock {stock.symbol} in the DB after technical analysis')


@background()
def technically_valid_stocks_main():
    candidate_stocks = Stock.objects.filter(Q(is_accelerated=True) | Q(is_eps_growth=True)).exclude(is_breakout=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidate_stocks)) as executor:
        executor.map(calc_stock_technical_validation, candidate_stocks)

import concurrent.futures

from background_task import background
from django.db.models import Q
from django.utils import timezone
from yahoofinancials import YahooFinancials

from stocks_tracker.models import Stock

STOCK_YEARLY_HIGH_MULTIPLIER = 0.75
STOCK_YEARLY_LOW_MULTIPLIER = 1.3
stocks = set()
BILION_IN_NUMBER = 1000000000
MILION_IN_NUMBER = 1000000
TRILION_IN_NUMBER = 1000000000000


def update_stocks_in_db():
    for stock in stocks:
        try:
            stock.save()
        except Exception as e:
            print(f'Failed to update stock {stock.symbol} in the DB: {str(e)}')


def is_stock_technically_valid(stock,our_stock_obj):
    if  (calculate_ps_to_next_year(stock, our_stock_obj)) == False:
        return False
    return True
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
        stock.is_technically_valid = is_stock_technically_valid(yahoo_stock,stock)
        stock.last_technically_valid_update = timezone.now()
        stocks.add(stock)
    except Exception as e:
        print(f'Failed to decide if stock {stock.symbol} in technically valid: {str(e)}')


def calculate_ps_to_next_year(yahoo_stock,our_stock_obj):
    market_cup = yahoo_stock.get_market_cap()
    ps_next_year_ratio  = 0
    target_avg_sales = 0
    if (our_stock_obj.target_avg_sales):
        if(our_stock_obj.target_avg_sales[-1]=='B'):
            target_avg_sales = float(our_stock_obj.target_avg_sales[:-1]) * BILION_IN_NUMBER
            ps_next_year_ratio = market_cup / target_avg_sales
        elif (our_stock_obj.target_avg_sales[-1]=='M'):
            target_avg_sales = float(our_stock_obj.target_avg_sales[:-1]) * MILION_IN_NUMBER
            ps_next_year_ratio = market_cup / target_avg_sales
        else:
            target_avg_sales = float(our_stock_obj.target_avg_sales[:-1]) * TRILION_IN_NUMBER
            ps_next_year_ratio = market_cup / target_avg_sales


        sales_growth_number = (float(our_stock_obj.target_sales_growth[:-1]))
        if ((sales_growth_number / 2)  >= ps_next_year_ratio)  :
            print(our_stock_obj.symbol)
            return True

    return False



def technically_valid_stocks_main():
    print('Started technically_valid_stocks_main')
    global stocks
    candidate_stocks = Stock.objects.filter((Q(is_eps_growth=True)  & Q(is_growth_potential=True )) ).exclude(is_breakout=True)
    print(candidate_stocks)
    if candidate_stocks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidate_stocks)) as executor:
            executor.map(calc_stock_technical_validation, candidate_stocks)
    update_stocks_in_db()
    print('Finished technically_valid_stocks_main')

from background_task import background
from django.utils import timezone

from stocks_tracker.models import Stock

QUARTERS_TO_FOLLOW_GROWTH = 3
QUARTERS_TO_FOLLOW_ACCELERATION = 2
EPS_GROWTH_THRESHOLD = 30
SALES_GROWTH_THRESHOLD = 40


def is_stock_in_eps_growth(eps_list):
    if not eps_list or len(eps_list) < QUARTERS_TO_FOLLOW_GROWTH:
        return False

    for quarter in range(QUARTERS_TO_FOLLOW_GROWTH * (-1), 0):
        if eps_list[quarter] < EPS_GROWTH_THRESHOLD:
            return False

    return True


def is_accelerating(data_list):
    if not data_list or len(data_list) < QUARTERS_TO_FOLLOW_ACCELERATION:
        return False

    for quarter in range(QUARTERS_TO_FOLLOW_ACCELERATION * (-1), 0):
        if data_list[quarter] <= 0 or (quarter < -1 and data_list[quarter] >= data_list[quarter + 1]):
            return False

    return True


def is_stock_in_acceleration(stock,duration):

    if (duration == 'q'):
        return is_accelerating(stock.net_income_growth_q) \
               and is_accelerating(stock.eps_growth_q) \
               and is_accelerating(stock.sales_growth_q)
    else:
         return is_accelerating(stock.net_income_growth_y) \
               and is_accelerating(stock.eps_growth_y) \
               and is_accelerating(stock.sales_growth_y)

def is_growth_potential(stock):

    if ((stock.target_sales_growth) and (stock.target_sales_growth != 'N/A')):
        sales_growth_number = (float(stock.target_sales_growth[:-1].replace(',','')))
    else:
        return False

    if (sales_growth_number>=SALES_GROWTH_THRESHOLD):
        return True

    return False


def update_stock_fields(stock):
    now = timezone.now()
    stock.is_growth_potential = is_growth_potential(stock)
    stock.is_accelerated_q = is_stock_in_acceleration(stock,'q')
    stock.is_accelerated_y = is_stock_in_acceleration(stock,'y')
    stock.is_eps_growth_q = is_stock_in_eps_growth(stock.eps_growth_q)
    stock.is_eps_growth_y = is_stock_in_eps_growth(stock.eps_growth_y)
    stock.last_rater_update = now
    if (stock.is_accelerated_q) and (stock.is_accelerated_y):
        print(stock.symbol)
    #if not stock.is_accelerated and not stock.is_eps_growth and not stock.is_growth_potential:
     #   stock.is_technically_valid = False
      #  stock.last_technically_valid_update = now


def stocks_rater_main():
    print('Started stocks_rater_main')
    stocks = Stock.objects.all()
    for stock in stocks:
        try:
            update_stock_fields(stock)
            stock.save()
        except:
            print(f'Failed to save stock {stock.symbol} in the DB after stock rater')
    print('Finished stocks_rater_main')
